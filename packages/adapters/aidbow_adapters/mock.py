"""离线可跑的 mock 适配器（测试 / 本地开发用，零网络、零密钥）。"""
from __future__ import annotations
from typing import Any


class MockLLMAdapter:
    """确定性 mock LLM：不联网、不随机，输出可复现。

    行为：
    - 默认回显器：把 prompt 以固定模板包裹返回（便于断言注入是否生效）。
    - 传入 `reply=prompt 模板字符串` 可自定义固定回复（`{prompt}`/`{system}` 占位）。
    - 传入 `script=[...]` 可按调用次序依次返回固定回复（超出次序后回落到模板）。
    """
    id = "mock-llm"

    def __init__(self, reply: str = "[mock] {prompt}", script: list[str] | None = None):
        self.reply = reply
        self.script = list(script or [])
        self.calls: list[dict[str, Any]] = []

    # —— SPEC/core 契约：generate()（供 harness 的 LLM 路径调用）——
    def generate(self, prompt: str, **kwargs: Any) -> str:
        return self.complete(prompt, **kwargs)

    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 1024,
                 **opts: Any) -> str:
        self.calls.append({"prompt": prompt, "system": system})
        if self.script:
            return self.script.pop(0)
        return self.reply.replace("{prompt}", prompt).replace("{system}", system or "")


class MockRetrievalAdapter:
    """确定性 mock 检索：在内存语料中做子串匹配打分，无结果返回空列表。"""
    id = "mock-retrieval"

    def __init__(self, corpus: list[tuple[str, str]] | None = None):
        # corpus: [(source, text), ...]
        self.corpus = list(corpus or [])

    def search(self, query: str, *, top_k: int = 5, **opts: Any) -> list[dict[str, Any]]:
        hits: list[dict[str, Any]] = []
        for source, text in self.corpus:
            score = text.count(query) if query else 0.0
            if query and query in text:
                score = max(score, 1.0)
            if score > 0:
                hits.append({"text": text, "score": float(score), "source": source})
        hits.sort(key=lambda h: -h["score"])
        return hits[:top_k]


__all__ = ["MockLLMAdapter", "MockRetrievalAdapter"]
