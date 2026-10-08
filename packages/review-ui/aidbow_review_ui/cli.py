"""review-ui 命令行：Idea[].json → 自包含评审 HTML。

用法：
    python -m aidbow_review_ui ideas.json -o review.html
    python -m aidbow_review_ui ideas.json --demand-id demo-001 --title "春季选题评审"

输入 JSON 顶层可为 Idea[] 或 {"demandId": ..., "ideas": [...]}；
使用后者且未显式传 --demand-id 时，自动采用文件中的 demandId。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .decision_export import build_decision, decision_to_json, decision_to_markdown
from .models import ReviewUIError, load_ideas
from .page import write_page


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ReviewUIError(f"无法读取输入文件 {path}：{exc}") from exc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="aidbow-review-ui",
        description="把 Idea[] 渲染成离线自包含的评审决策台 HTML。",
    )
    ap.add_argument("input", help="Idea[].json（顶层数组或 {'demandId','ideas'}）")
    ap.add_argument("-o", "--out", help="输出 HTML 路径（默认 <input同名>.review.html）")
    ap.add_argument("--demand-id", default="", help="Decision.demandId（默认取输入文件中的 demandId）")
    ap.add_argument("--title", default="", help="页面标题（默认用 demandId）")
    ap.add_argument("--print-markdown", metavar="STATE.json",
                    help="离线模式：按给定评审状态导出决策单 Markdown 后退出")
    ap.add_argument("--print-json", metavar="STATE.json",
                    help="离线模式：按给定评审状态导出 Decision JSON 后退出")
    args = ap.parse_args(argv)

    try:
        in_path = Path(args.input)
        raw = _read_json(in_path)
        demand_id = args.demand_id
        if isinstance(raw, dict) and not demand_id:
            demand_id = str(raw.get("demandId", in_path.stem))
        if not demand_id:
            demand_id = in_path.stem
        ideas = load_ideas(raw) if isinstance(raw, list) else load_ideas(raw.get("ideas", []))

        if args.print_markdown or args.print_json:
            state_path = Path(args.print_markdown or args.print_json)
            store = json.loads(state_path.read_text(encoding="utf-8"))
            if args.print_json:
                print(decision_to_json(build_decision(ideas, store, demand_id)))
            else:
                print(decision_to_markdown(ideas, store, demand_id))
            return 0

        out_path = Path(args.out) if args.out else in_path.with_suffix(".review.html")
        write_page(ideas, demand_id, out_path, title=args.title or demand_id)
        print(f"OK 生成 {out_path}（{len(ideas)} 条创意）")
        return 0
    except ReviewUIError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
