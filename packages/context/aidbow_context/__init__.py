# -*- coding: utf-8 -*-
"""aidbow_context — 上下文解析（实现 aidbow_core.ContextProvider）。"""
from .providers import TextProvider, LinkProvider, FileProvider
from .registry import ContextRegistry

__all__ = ["TextProvider", "LinkProvider", "FileProvider", "ContextRegistry"]
__version__ = "0.1.0"
