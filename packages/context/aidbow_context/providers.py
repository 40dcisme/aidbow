# -*- coding: utf-8 -*-
"""基础 ContextProvider 实现：text（内联） / link（URL 抓取） / file（本地文件）。

依赖：仅标准库（urllib/re/html）。**离线不可用时不编造**：返回空文本并把原因记入 meta。
"""
import html as _html
import os
import re
import urllib.request

try:
    from aidbow_core import ContextItem, ResolvedContext
    _CORE = True
except Exception:                                   # 本地无 core 时兜底
    _CORE = False
    class ContextItem(object):
        def __init__(self, kind="", ref="", meta=None):
            self.kind, self.ref, self.meta = kind, ref, meta or {}
    class ResolvedContext(object):
        def __init__(self, text="", citations=None, meta=None):
            self.text, self.citations, self.meta = text, citations or [], meta or {}


def _strip_html(s):
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = _html.unescape(s)
    return re.sub(r"[ \t\r\f\v]+", " ", re.sub(r"\n\s*\n+", "\n\n", s)).strip()


class TextProvider(object):
    """内联文本：ref 即文本内容。"""
    id = "text"

    def canHandle(self, item):
        return getattr(item, "kind", "") == "text"

    def resolve(self, item, ctx=None):
        return ResolvedContext(text=str(getattr(item, "ref", "")),
                               citations=[], meta={"provider": self.id})


class FileProvider(object):
    """本地文件：ref 为路径。"""
    id = "file"

    def canHandle(self, item):
        return getattr(item, "kind", "") == "file"

    def resolve(self, item, ctx=None):
        path = getattr(item, "ref", "")
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            return ResolvedContext(text=text, citations=[path], meta={"provider": self.id})
        except Exception as e:                      # 不编造：如实记录失败
            return ResolvedContext(text="", citations=[], meta={"provider": self.id, "error": str(e)})


class LinkProvider(object):
    """URL 抓取：ref 为 http(s) 链接。仅标准库；离线/失败时如实记录，不编造。"""
    id = "link"
    TIMEOUT = 10

    def canHandle(self, item):
        return getattr(item, "kind", "") == "link"

    def resolve(self, item, ctx=None):
        url = getattr(item, "ref", "")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "aidbow-context/0.1"})
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
            return ResolvedContext(text=_strip_html(raw), citations=[url],
                                   meta={"provider": self.id, "status": "ok"})
        except Exception as e:
            return ResolvedContext(text="", citations=[], meta={"provider": self.id, "error": str(e)})
