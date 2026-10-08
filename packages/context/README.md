# @aidbow/context

> 上下文解析：实现 `aidbow_core.ContextProvider`。基础 provider：**text / link / file**，可插件式扩展。

**状态**：✅ v0.1.0

## 用法
```python
from aidbow_context import ContextRegistry
from aidbow_core import ContextItem

reg = ContextRegistry()                       # 默认 text/link/file
rc = reg.resolve(ContextItem(kind="file", ref="/path/a.md"))
print(rc.text[:80], rc.citations)             # 解析结果 + 来源引用
```

## 插件式扩展（闭源覆盖点）
```python
reg.register(MyVerticalProvider(), front=True)   # 同 `canHandle` 契约，无需 fork
```

## 红线
- 解析失败**不编造**：返回空文本并把原因写入 `meta['error']`。
- 仅标准库；`link` 抓取超时/离线时如实失败。
