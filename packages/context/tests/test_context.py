# -*- coding: utf-8 -*-
"""context 单测：协议一致性 + 三类 provider + 分派 + 插件注册 + 离线不编造。"""
import os
import sys
import tempfile
_HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_HERE, ".."))
sys.path.insert(0, os.path.join(_HERE, "..", "..", "core"))
from aidbow_core import ContextItem, ContextProvider, ResolvedContext
from aidbow_context import TextProvider, LinkProvider, FileProvider, ContextRegistry


def test_providers_implement_protocol():
    assert isinstance(TextProvider(), ContextProvider)
    assert isinstance(LinkProvider(), ContextProvider)
    assert isinstance(FileProvider(), ContextProvider)


def test_text_provider():
    rc = TextProvider().resolve(ContextItem(kind="text", ref="hello 上下文"))
    assert rc.text == "hello 上下文" and rc.meta["provider"] == "text"


def test_file_provider(tmp=None):
    d = tempfile.mkdtemp()
    p = os.path.join(d, "a.txt")
    open(p, "w", encoding="utf-8").write("文件内容")
    rc = FileProvider().resolve(ContextItem(kind="file", ref=p))
    assert rc.text == "文件内容" and rc.citations == [p]


def test_file_provider_missing_does_not_fabricate():
    rc = FileProvider().resolve(ContextItem(kind="file", ref="/no/such/file"))
    assert rc.text == "" and "error" in rc.meta


def test_link_offline_no_fabrication():
    # 无效域名 → 应失败但不编造
    rc = LinkProvider().resolve(ContextItem(kind="link", ref="http://nonexistent.invalid.local/x"))
    assert rc.text == "" and "error" in rc.meta


def test_registry_dispatch_and_plugin():
    reg = ContextRegistry()
    assert reg.pick(ContextItem(kind="text", ref="x")).id == "text"
    assert reg.pick(ContextItem(kind="file", ref="x")).id == "file"
    # 插件：自定义 kind 优先匹配
    class MyProvider(object):
        id = "my"
        def canHandle(self, item): return getattr(item, "kind", "") == "dataset"
        def resolve(self, item, ctx=None): return ResolvedContext(text="DS", citations=["ds://1"], meta={})
    reg.register(MyProvider(), front=True)
    rc = reg.resolve(ContextItem(kind="dataset", ref="ds://1"))
    assert rc.text == "DS"


def test_registry_unknown_kind():
    reg = ContextRegistry()
    rc = reg.resolve(ContextItem(kind="???", ref="x"))
    assert rc.text == "" and "error" in rc.meta


if __name__ == "__main__":
    import run_tests
    raise SystemExit(run_tests.main(os.path.dirname(__file__)))
