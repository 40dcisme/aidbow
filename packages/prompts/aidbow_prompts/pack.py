"""PromptPack 实现 + 覆盖机制（SPEC §2.4 / §3）。

覆盖顺序：项目覆盖目录 → base 包（同名覆盖，后者不覆盖前者）。
"""
from __future__ import annotations
import os, re
from string import Template

try:
    from aidbow_core import PromptPack  # noqa
except Exception:
    pass

BASE_DIR = os.path.join(os.path.dirname(__file__), "base")


def load_dir(path: str) -> dict[str, str]:
    """载入目录下 *.txt|*.md 为 {模板名: 文本}（模板名=去扩展名的文件名）。"""
    out: dict[str, str] = {}
    if not path or not os.path.isdir(path):
        return out
    for fn in sorted(os.listdir(path)):
        if fn.endswith((".txt", ".md")):
            name = os.path.splitext(fn)[0]
            with open(os.path.join(path, fn), encoding="utf-8") as f:
                out[name] = f.read()
    return out


class BasePromptPack:
    """基础包；`overlay_dir` 提供项目覆盖（闭源精炼提示词放这里）。"""
    id = "base"

    def __init__(self, overlay_dir: str | None = None, overlay: dict[str, str] | None = None):
        self.templates = load_dir(BASE_DIR)
        if overlay_dir:
            self.templates.update(load_dir(overlay_dir))     # 项目覆盖 base
        if overlay:
            self.templates.update(overlay)

    def get(self, name: str, vars: dict[str, str] | None = None) -> str:
        if name not in self.templates:
            raise KeyError(f"prompt template '{name}' not found")
        tpl = self.templates[name]
        # 同时支持 ${var} 与 {{var}} 两种占位
        out = Template(tpl).safe_substitute(vars or {}) if "$" in tpl else tpl
        if vars:
            for k, v in vars.items():
                out = out.replace("{{" + k + "}}", str(v))
        return out
