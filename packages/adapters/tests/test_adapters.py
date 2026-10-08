"""adapters 单测（零依赖，无 pytest 也可跑）。

覆盖验收点：
① LLMAdapter 接口定义并对齐 HarnessContext 用法（runtime_checkable + 注入）
② 离线可跑的 mock 适配器 + 真实 provider 骨架
③ 单测可注入替换（注入 mock 后 harness 行为受控）
④ 无密钥硬编码（凭据走环境变量；未配置显式报错）
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))
from aidbow_core import HarnessContext
from aidbow_adapters import (
    LLMAdapter, RetrievalAdapter, MockLLMAdapter, MockRetrievalAdapter,
    OpenAICompatAdapter, AdapterNotConfigured, AdapterRequestError,
)


# ---------- ① 接口契约 ----------
def test_mock_llm_implements_protocol():
    assert isinstance(MockLLMAdapter(), LLMAdapter)

def test_openai_compat_implements_protocol():
    a = OpenAICompatAdapter(base_url="https://example.invalid/v1", model="m")
    assert isinstance(a, LLMAdapter)

def test_mock_retrieval_implements_protocol():
    assert isinstance(MockRetrievalAdapter(), RetrievalAdapter)

def test_llm_adapter_injects_into_harness_context():
    llm = MockLLMAdapter()
    ctx = HarnessContext(llm=llm)
    assert ctx.llm is llm


# ---------- ② mock：确定性、离线 ----------
def test_mock_llm_echo_template():
    llm = MockLLMAdapter(reply="E:{prompt}|S:{system}")
    out = llm.complete("hello", system="sys")
    assert out == "E:hello|S:sys"

def test_mock_llm_script_sequence_then_fallback():
    llm = MockLLMAdapter(reply="FALLBACK", script=["first", "second"])
    assert llm.complete("a") == "first"
    assert llm.complete("b") == "second"
    assert llm.complete("c") == "FALLBACK"
    assert len(llm.calls) == 3

def test_mock_retrieval_scores_and_tops():
    r = MockRetrievalAdapter(corpus=[
        ("doc1", "增长 实验增长 复盘"),
        ("doc2", "无关内容"),
        ("doc3", "增长"),
    ])
    hits = r.search("增长", top_k=2)
    assert [h["source"] for h in hits] == ["doc1", "doc3"]
    assert hits[0]["score"] > hits[1]["score"]
    assert r.search("完全不存在") == []

def test_mock_retrieval_empty_query_returns_empty():
    assert MockRetrievalAdapter(corpus=[("d", "x")]).search("") == []


# ---------- ② 真实 provider 骨架：请求构造 / 响应解析 / 错误路径 ----------
def _adapter():
    return OpenAICompatAdapter(base_url="https://api.example/v1/", model="test-model")

def test_prepare_request_shape():
    a = _adapter()
    url, headers, payload = a._prepare_request(
        "hi", system="sys", temperature=0.2, max_tokens=8, api_key="KEY")
    assert url == "https://api.example/v1/chat/completions"
    assert headers["Authorization"] == "Bearer KEY"
    assert payload["model"] == "test-model"
    assert payload["messages"][0] == {"role": "system", "content": "sys"}
    assert payload["messages"][1] == {"role": "user", "content": "hi"}
    assert payload["temperature"] == 0.2 and payload["max_tokens"] == 8

def test_prepare_request_no_system_and_trailing_slash():
    url, _, payload = _adapter()._prepare_request("q", system=None, temperature=0.7,
                                                  max_tokens=8, api_key="K")
    assert url.endswith("/chat/completions")
    assert [m["role"] for m in payload["messages"]] == ["user"]

def test_extract_text_openai_shape():
    assert _adapter()._extract_text({"choices": [{"message": {"content": "ok"}}]}) == "ok"

def test_extract_text_bad_shape_raises():
    try:
        _adapter()._extract_text({"nope": 1})
        assert False, "should raise"
    except AdapterRequestError:
        pass

def test_missing_api_key_env_raises_not_configured(monkeypatch=None):
    os.environ.pop("AIDBOW_TEST_NOKEY", None)
    a = OpenAICompatAdapter(base_url="https://x/v1", model="m", api_key_env="AIDBOW_TEST_NOKEY")
    try:
        a.complete("p")
        assert False, "should raise"
    except AdapterNotConfigured:
        pass

def test_no_secret_hardcoded():
    # ④ 无密钥硬编码：源码中不出现 sk- 形态密钥
    import pathlib
    pkg = pathlib.Path(__file__).resolve().parent.parent / "aidbow_adapters"
    for f in pkg.glob("*.py"):
        assert "sk-" not in f.read_text(encoding="utf-8"), f"{f.name} 含硬编码密钥"


# ---------- ③ 注入替换：注入 mock 后，自定义步骤经 ctx.llm 拿到受控产出 ----------
def test_injected_llm_drives_custom_step_via_harness():
    # 不改动兄弟包（extension over fork）：用自定义 StepContract 展示 llm 注入路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "harness"))
    from aidbow_harness import BaseHarness
    from aidbow_core import Demand

    class LlmBrainstormStep:
        """示例步骤：ctx.llm 存在时调用它生成创意（含 fallback 占位，不编造）。"""
        name = "brainstorm"
        def run(self, input, ctx):
            demand = input if hasattr(input, "id") else input.get("demand")
            if ctx.llm is None:
                return {"demand": demand, "ideas": []}
            text = ctx.llm.complete("围绕需求各出 1 条创意", system="brainstorm")
            idea = {"id": "llm:1", "author": "llm", "body": text}
            return {"demand": demand, "ideas": [idea]}

    llm = MockLLMAdapter(reply="IDEA-FROM-LLM")
    h = BaseHarness(llm=llm, stages=[("brainstorm", LlmBrainstormStep())])
    out = h.run(Demand(id="d1", prompt="x"))
    assert llm.calls, "注入的 llm 应被调用"
    assert out["trace"] == ["brainstorm"]
    assert out["result"]["ideas"][0]["body"] == "IDEA-FROM-LLM"


# ---------- 自定义 provider 覆盖钩子（extension over fork） ----------
def test_provider_override_via_hook():
    class AnthropicStyle(OpenAICompatAdapter):
        id = "anthropic-style"
        def _prepare_request(self, prompt, *, system, temperature, max_tokens,
                             api_key, **opts):
            return ("https://api.example/v1/messages",
                    {"x-api-key": api_key},
                    {"model": self.model,
                     "messages": [{"role": "user", "content": prompt}],
                     "system": system or ""})
    a = AnthropicStyle(base_url="https://api.example/v1", model="m",
                       api_key_env="AIDBOW_TEST_NOKEY2")
    os.environ.pop("AIDBOW_TEST_NOKEY2", None)
    try:
        a.complete("p")
        assert False, "should raise"
    except AdapterNotConfigured:
        pass
