# @aidbow/adapters

> 适配器 —— LLM provider / 检索 / 上下文源 可插拔适配器

**状态**：✅ 可用（v0.1.0）

## 归属
- 开源基础能力；依赖上游 `aidbow-core`（仅数据模型与协议概念）。
- 被 `harness` / `context` 通过 `HarnessContext.llm` 等注入点使用（SPEC §2.2 / §4 依赖方向）。

## 公开 API
与 `../../SPEC.md` 扩展点契约一致：

| 类型 | 说明 |
|---|---|
| `LLMAdapter`（Protocol） | SPEC §2.2 `HarnessContext.llm` 注入点；`complete(prompt, *, system, temperature, max_tokens) -> str` |
| `RetrievalAdapter`（Protocol） | 检索扩展点；`search(query, *, top_k) -> list[{text, score, source}]` |
| `MockLLMAdapter` | 离线确定性 mock：回显模板或按 `script` 依次返回；记录调用便于断言 |
| `MockRetrievalAdapter` | 离线确定性 mock：内存语料子串匹配打分 |
| `OpenAICompatAdapter` | 真实 provider 骨架（OpenAI 兼容 Chat Completions，stdlib urllib 传输）；子类覆盖 `_prepare_request()` 适配其他 provider |
| `AdapterNotConfigured` | 环境变量未提供凭据时抛出 |
| `AdapterRequestError` | 网络 / HTTP / 响应形态异常时抛出 |

## 红线（AGENTS.md）
- 零第三方运行时依赖（stdlib only）。
- 凭据只从环境变量读取（默认 `AIDBOW_LLM_API_KEY`，可用 `api_key_env` 自定），**绝不硬编码**。
- 失败显式抛错 / 空结果返回空列表，**不编造内容**。

## 快速开始
```python
from aidbow_adapters import MockLLMAdapter, OpenAICompatAdapter, LLMAdapter
from aidbow_core import HarnessContext

# 1) 离线测试：mock 注入 HarnessContext
llm = MockLLMAdapter(reply="[mock] {prompt}")
assert isinstance(llm, LLMAdapter)
ctx = HarnessContext(llm=llm)

# 2) 真实 provider（先 export AIDBOW_LLM_API_KEY=...）
llm = OpenAICompatAdapter(base_url="https://api.openai.com/v1", model="gpt-4o-mini")
text = llm.complete("用一句话介绍 DBOW")
```

## 测试
```bash
python packages/adapters/run_tests.py        # 单包
python run_all_tests.py                      # 全仓（含本包）
```
