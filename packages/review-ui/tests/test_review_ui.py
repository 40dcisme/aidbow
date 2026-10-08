"""review-ui 单元测试 —— 零三方依赖，python packages/review-ui/run_tests.py。"""
import json
import pathlib
import re
import sys
import tempfile
import unittest

PKG_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG_DIR))

from aidbow_review_ui import (  # noqa: E402
    ReviewUIError,
    load_ideas,
    normalize_idea,
    render_page,
    write_page,
    build_decision,
    decision_to_json,
    decision_to_markdown,
    validate_decision,
)
from aidbow_review_ui.cli import main as cli_main  # noqa: E402

DEMO = PKG_DIR / "examples" / "ideas.demo.json"


def good_idea(**over):
    base = {
        "id": "x:01",
        "author": "x",
        "round": "R1",
        "title": "t",
        "oneLiner": "o",
        "body": "b",
        "P": {"P1": 4},
        "basis": {"P1": "why"},
    }
    base.update(over)
    return base


class TestNormalize(unittest.TestCase):
    def test_ok_minimal(self):
        out = normalize_idea(good_idea())
        self.assertEqual(out["id"], "x:01")
        self.assertEqual(out["P"], {"P1": 4})

    def test_missing_fields(self):
        raw = good_idea()
        del raw["title"]
        with self.assertRaisesRegex(ReviewUIError, "title"):
            normalize_idea(raw)

    def test_bad_round(self):
        with self.assertRaisesRegex(ReviewUIError, "round"):
            normalize_idea(good_idea(round="R9"))

    def test_empty_id(self):
        with self.assertRaisesRegex(ReviewUIError, "id"):
            normalize_idea(good_idea(id="  "))

    def test_bad_p_range(self):
        with self.assertRaisesRegex(ReviewUIError, "P3"):
            normalize_idea(good_idea(**{"P": {"P3": 9}}))

    def test_p_bool_rejected(self):
        # bool 是 int 子类，必须显式拒绝。
        with self.assertRaises(ReviewUIError):
            normalize_idea(good_idea(**{"P": {"P3": True}}))

    def test_unknown_p_dimension(self):
        with self.assertRaises(ReviewUIError):
            normalize_idea(good_idea(**{"P": {"P9": 3}}))

    def test_bad_basis_type(self):
        with self.assertRaises(ReviewUIError):
            normalize_idea(good_idea(**{"basis": {"P1": 5}}))

    def test_lineage_validation(self):
        with self.assertRaises(ReviewUIError):
            normalize_idea(good_idea(lineage={"from": "y:01", "mode": "copy"}))
        out = normalize_idea(good_idea(lineage={"from": "y:01", "mode": "graft"}))
        self.assertEqual(out["lineage"]["mode"], "graft")

    def test_not_dict(self):
        with self.assertRaises(ReviewUIError):
            normalize_idea("nope")  # type: ignore[arg-type]


class TestLoad(unittest.TestCase):
    def test_demo_file(self):
        ideas = load_ideas(DEMO)
        self.assertEqual(len(ideas), 4)
        rounds = {it["round"] for it in ideas}
        self.assertEqual(rounds, {"R1", "R2"})

    def test_list_input(self):
        self.assertEqual(len(load_ideas([good_idea()])), 1)

    def test_object_wrapper(self):
        ideas = load_ideas([good_idea()])
        self.assertEqual(ideas[0]["author"], "x")

    def test_duplicate_ids(self):
        with self.assertRaisesRegex(ReviewUIError, "唯一"):
            load_ideas([good_idea(), good_idea()])

    def test_missing_file(self):
        with self.assertRaises(ReviewUIError):
            load_ideas("/no/such/file.json")

    def test_bad_json(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "x.json"
            p.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ReviewUIError):
                load_ideas(p)

    def test_wrong_top_level(self):
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td) / "x.json"
            p.write_text('"a string"', encoding="utf-8")
            with self.assertRaises(ReviewUIError):
                load_ideas(p)


class TestDecision(unittest.TestCase):
    def setUp(self):
        self.ideas = load_ideas(DEMO)
        self.ids = [it["id"] for it in self.ideas]

    def test_empty_decision(self):
        d = build_decision(self.ideas, {}, "demo-park-weekend")
        self.assertEqual(d["selected"], [])
        self.assertNotIn("priorities", d)
        self.assertNotIn("notes", d)

    def test_full_decision(self):
        store = {
            "alpha:01": {"picked": True, "priority": "P0", "note": "先做这个 "},
            "alpha:02": {"picked": False, "priority": "shelved", "note": ""},
            "beta:01": {"picked": True, "priority": "P1", "note": "同做"},
        }
        d = build_decision(self.ideas, store, "demo-park-weekend")
        self.assertEqual(d["selected"], ["alpha:01", "beta:01"])
        self.assertEqual(d["priorities"]["alpha:02"], "shelved")
        # 空白 note 不入库；非空白被 strip。
        self.assertEqual(d["notes"]["alpha:01"], "先做这个")
        self.assertNotIn("alpha:02", d["notes"])

    def test_validate_unknown_selected(self):
        with self.assertRaises(ReviewUIError):
            validate_decision(
                {"demandId": "d", "selected": ["ghost:1"]}, self.ids
            )

    def test_validate_bad_priority(self):
        with self.assertRaises(ReviewUIError):
            validate_decision(
                {"demandId": "d", "selected": [],
                 "priorities": {"alpha:01": "P9"}},
                self.ids,
            )

    def test_json_roundtrip(self):
        store = {"alpha:01": {"picked": True, "priority": "P0", "note": "go"}}
        d = build_decision(self.ideas, store, "demo-park-weekend")
        again = json.loads(decision_to_json(d))
        self.assertEqual(again, d)

    def test_markdown_sections(self):
        store = {
            "alpha:01": {"picked": True, "priority": "P0", "note": "go"},
            "alpha:02": {"picked": False, "priority": "shelved", "note": ""},
            "beta:02": {"picked": True, "priority": "P1", "note": ""},
        }
        md = decision_to_markdown(self.ideas, store, "demo-park-weekend")
        self.assertIn("✅ 选中（纳入执行候选）（2）", md)
        self.assertIn("⏸ 搁置（1）", md)
        self.assertIn("go", md)
        self.assertIn("deepen ← beta:01", md)  # R2 选中卡呈现递进来源

    def test_markdown_empty_warning(self):
        md = decision_to_markdown(self.ideas, {}, "demo-park-weekend")
        self.assertIn("尚未做出任何决策", md)


class TestPage(unittest.TestCase):
    def setUp(self):
        self.ideas = load_ideas(DEMO)

    def test_page_self_contained(self):
        html = render_page(self.ideas, "demo-park-weekend")
        # 零外链：不得出现 http(s) 资源引用或外链标签。
        self.assertNotRegex(html, r'(src|href)\s*=\s*["\']https?://')
        # 数据在页面内。
        self.assertIn("晨间瑜伽", html)
        self.assertIn("alpha:01", html)
        # app.js 内联（标志性函数片段）。
        self.assertIn("buildMarkdown", html)
        # 样式内联。
        self.assertIn("--acc", html)

    def test_page_card_count_placeholders_filled(self):
        html = render_page(self.ideas, "demo-park-weekend")
        self.assertNotIn("__TITLE__", html)
        self.assertNotIn("__DATA_JSON__", html)
        self.assertNotIn("__APP_JS__", html)

    def test_xss_escape_in_data(self):
        evil = [normalize_idea(good_idea(
            id="z:01", title="<script>alert(1)</script>", body="x"))]
        html = render_page(evil, "d")
        # 数据经 ensure_ascii 转义 <，无原始 script 注入。
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_write_page(self):
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "nested" / "r.html"
            write_page(self.ideas, "demo-park-weekend", out)
            self.assertTrue(out.exists())
            self.assertGreater(out.stat().st_size, 1000)


class TestCLI(unittest.TestCase):
    def test_build_cli(self):
        with tempfile.TemporaryDirectory() as td:
            out = pathlib.Path(td) / "r.html"
            rc = cli_main([str(DEMO), "-o", str(out)])
            self.assertEqual(rc, 0)
            self.assertTrue(out.exists())

    def test_cli_bad_input(self):
        rc = cli_main(["/no/such/file.json"])
        self.assertEqual(rc, 2)

    def test_cli_export_json(self):
        import io
        import contextlib

        with tempfile.TemporaryDirectory() as td:
            state = pathlib.Path(td) / "s.json"
            state.write_text(json.dumps(
                {"alpha:01": {"picked": True, "priority": "P0", "note": "go"}}
            ), encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = cli_main([str(DEMO), "--print-json", str(state)])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["selected"], ["alpha:01"])


if __name__ == "__main__":
    unittest.main()
