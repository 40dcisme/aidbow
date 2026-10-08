# -*- coding: utf-8 -*-
"""ContextRegistry — 插件式上下文解析：按 canHandle 分派到已注册 provider。

用法：
    reg = ContextRegistry()                      # 默认带 text/link/file
    reg.register(MyProvider())                   # 注册垂类 provider（闭源扩展点）
    rc = reg.resolve(ContextItem(kind="link", ref="https://..."))
"""
try:
    from aidbow_core import ContextProvider  # noqa
except Exception:
    ContextProvider = object

from .providers import TextProvider, LinkProvider, FileProvider


class ContextRegistry(object):
    def __init__(self, providers=None):
        self.providers = list(providers) if providers is not None else             [TextProvider(), LinkProvider(), FileProvider()]

    def register(self, provider, front=False):
        """注册 provider；front=True 时插到最前（优先匹配）。"""
        if front:
            self.providers.insert(0, provider)
        else:
            self.providers.append(provider)
        return provider

    def pick(self, item):
        for p in self.providers:
            try:
                if p.canHandle(item):
                    return p
            except Exception:
                continue
        return None

    def resolve(self, item, ctx=None):
        p = self.pick(item)
        if p is None:
            from aidbow_core import ResolvedContext
            return ResolvedContext(text="", citations=[],
                                   meta={"error": "no provider for kind=%s" % getattr(item, "kind", "?")})
        return p.resolve(item, ctx)
