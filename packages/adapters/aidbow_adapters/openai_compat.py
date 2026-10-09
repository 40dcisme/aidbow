"""通用 LLM 适配器骨架（真实 provider）。

设计（对齐 SPEC §3「覆盖机制」与 AGENTS.md）：
- 零第三方依赖：传输用标准库 urllib；不内置任何 SDK。
- 凭据一律来自环境变量（`api_key_env` 指定），**绝不硬编码**（AGENTS.md §5 红线）。
- 未配置 / 网络失败 → 抛出明确异常，**不编造内容、不静默吞错**。
- 各 provider 差异通过 `_prepare_request()` 钩子覆盖，不改主流程（extension over fork）。
"""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from typing import Any


class AdapterNotConfigured(RuntimeError):
    """环境变量未提供凭据时抛出（显式失败，禁止编造）。"""


class AdapterRequestError(RuntimeError):
    """网络 / HTTP 失败时抛出。"""


class OpenAICompatAdapter:
    """OpenAI 兼容 Chat Completions 适配器骨架（覆盖多数自建/第三方 provider）。

    参数：
    - base_url: 服务根址（如 https://api.openai.com/v1）
    - model: 模型名
    - api_key_env: 存放 API key 的环境变量名（默认 AIDBOW_LLM_API_KEY）
    - timeout: 请求超时秒数

    子类化换 provider：覆盖 `_prepare_request()` 返回 (url, headers, payload)。
    """

    id = "openai-compat"

    def __init__(self, base_url: str, model: str,
                 api_key_env: str = "AIDBOW_LLM_API_KEY", timeout: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key_env = api_key_env
        self.timeout = timeout

    # ---- 主流程 ----
    # —— SPEC/core 契约：generate() 委托 complete()（满足 HarnessContext.llm 注入）——
    def generate(self, prompt: str, **kwargs: Any) -> str:
        return self.complete(prompt, **kwargs)

    def complete(self, prompt: str, *, system: str | None = None,
                 temperature: float = 0.7, max_tokens: int = 1024,
                 **opts: Any) -> str:
        key = self._api_key()
        url, headers, payload = self._prepare_request(
            prompt, system=system, temperature=temperature,
            max_tokens=max_tokens, api_key=key, **opts)
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise AdapterRequestError(f"HTTP {e.code} from {url}: {detail}") from e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            raise AdapterRequestError(f"network error calling {url}: {e}") from e
        return self._extract_text(data)

    # ---- provider 定制钩子 ----
    def _prepare_request(self, prompt: str, *, system: str | None, temperature: float,
                         max_tokens: int, api_key: str, **opts: Any) -> tuple[str, dict, dict]:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        payload.update(opts.pop("extra_payload", {}))
        return f"{self.base_url}/chat/completions", headers, payload

    # ---- 响应解析 / 凭据 ----
    def _extract_text(self, data: dict[str, Any]) -> str:
        # OpenAI 兼容：choices[0].message.content；其余形态显式报错（不猜）
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise AdapterRequestError(f"unexpected response shape: {json.dumps(data)[:500]}") from e

    def _api_key(self) -> str:
        key = os.environ.get(self.api_key_env, "")
        if not key:
            raise AdapterNotConfigured(
                f"environment variable {self.api_key_env!r} is not set; "
                f"set it before using {self.__class__.__name__}")
        return key


__all__ = ["OpenAICompatAdapter", "AdapterNotConfigured", "AdapterRequestError"]
