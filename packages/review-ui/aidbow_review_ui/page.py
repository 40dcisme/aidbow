"""自包含评审页生成器 —— 模板 + Idea[] + app.js → 单个离线 HTML。

生成的页面：
  - 全部 CSS / JS 内联，零外链，双击即可离线使用；
  - 数据以内联 <script type="application/json"> 承载（避免 </script> 注入问题
    由 json.dump 转义 "<" 为 \\u003c 解决）。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

_STATIC = Path(__file__).resolve().parent / "static"


def _safe_json(data: Any) -> str:
    # 保留中文原文（便于直接审阅 HTML），只定向转义可能闭合 <script> 的字符；
    # U+2028/2029 在 <script> 中是合法 JSON 但非法 JS，一并转义。
    s = json.dumps(data, ensure_ascii=False)
    table = {"<": "\\u003c", ">": "\\u003e", "&": "\\u0026",
             "\u2028": "\\u2028", "\u2029": "\\u2029"}
    return "".join(table.get(c, c) for c in s)


def render_page(
    ideas: List[Dict[str, Any]],
    demand_id: str,
    *,
    title: str = "",
) -> str:
    """返回完整 HTML 字符串。ideas 须先经 models.normalize_idea 校验。"""
    tmpl = (_STATIC / "index.html").read_text(encoding="utf-8")
    app_js = (_STATIC / "app.js").read_text(encoding="utf-8")

    page_title = title or demand_id
    html = (
        tmpl.replace("__TITLE__", page_title)
        .replace("__DEMAND_ID__", demand_id)
        .replace("__N__", str(len(ideas)))
        .replace("__DATA_JSON__", _safe_json(ideas))
        .replace("__APP_JS__", app_js)
    )
    return html


def write_page(
    ideas: List[Dict[str, Any]],
    demand_id: str,
    out_path: Path,
    *,
    title: str = "",
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_page(ideas, demand_id, title=title), encoding="utf-8")
    return out
