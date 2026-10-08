"""aidbow_review_ui — 评审决策台组件（离线自包含，零三方依赖）。

公共 API：
    load_ideas(path|list) -> Idea[]           加载并校验 SPEC §1 Idea
    render_page(ideas, demand_id) -> html     生成自包含评审页
    write_page(ideas, demand_id, path)        写入 HTML 文件
    build_decision(ideas, store, demand_id)   状态 → SPEC §1 Decision
    decision_to_markdown / decision_to_json   决策单导出
"""
from .models import (
    ReviewUIError,
    load_ideas,
    normalize_idea,
    validate_decision,
    P_KEYS,
    PRIORITIES,
)
from .page import render_page, write_page
from .decision_export import (
    build_decision,
    decision_to_json,
    decision_to_markdown,
)

__all__ = [
    "ReviewUIError",
    "load_ideas",
    "normalize_idea",
    "validate_decision",
    "P_KEYS",
    "PRIORITIES",
    "render_page",
    "write_page",
    "build_decision",
    "decision_to_json",
    "decision_to_markdown",
]
__version__ = "0.1.0"
