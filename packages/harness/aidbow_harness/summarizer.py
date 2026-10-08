# -*- coding: utf-8 -*-
"""Overview 自动化：人审之外的 LLM / Agent 两条收敛路径（同一 OverviewResult 契约）。

- LLM 路径（BaseOverviewLLM）：需 `llm` 适配器 + `prompts` 包；把创意集喂给提示词模板。
- Agent 路径（AgentOverview）：需 `agent` 适配器；把**整包上下文**交给另一个 Agent 读。
- 两条路径都**只归纳实际出现的内容、必须带 idea_id 溯源、跨专业冲突显式标记**（不编造）。

`BaseHarness` 的 overview 步骤若注入 `summarizer`，则自动产出 OverviewResult。
"""
from __future__ import annotations
import json

try:
    from aidbow_core import OverviewResult, OverviewCluster, OverviewConflict
except Exception:  # 本地无 core 时的兜底
    class OverviewResult:  # type: ignore
        def __init__(self, **k): self.__dict__.update(k)
    class OverviewCluster:  # type: ignore
        def __init__(self, **k): self.__dict__.update(k)
    class OverviewConflict:  # type: ignore
        def __init__(self, **k): self.__dict__.update(k)


def _ideas_brief(ideas):
    """把创意压成提示词友好的简报（标题 + 一句话核心 + 正文节选 + P），控制 token。"""
    out = []
    for it in ideas:
        g = (lambda k: getattr(it, k, None)) if not isinstance(it, dict) else (lambda k: it.get(k))
        out.append({
            "id": g("id"), "title": g("title"), "one": g("oneLiner") or g("one"),
            "body": (g("body") or "")[:1200], "P": g("P") or {},
        })
    return out


def _coerce(data, demand_id, method, provenance):
    """把 LLM/Agent 返回的 dict 规整为 OverviewResult（缺字段不臆造）。"""
    clusters = [OverviewCluster(label=c.get("label", ""), note=c.get("note", ""),
                                idea_ids=list(c.get("idea_ids", [])))
                for c in data.get("clusters", [])]
    conflicts = [OverviewConflict(term=c.get("term", ""), statements=list(c.get("statements", [])))
                 for c in data.get("conflicts", [])]
    return OverviewResult(
        demandId=demand_id, method=method, clusters=clusters, conflicts=conflicts,
        shortlist=list(data.get("shortlist", [])), open_questions=list(data.get("open_questions", [])),
        warnings=list(data.get("warnings", [])), provenance=provenance)


def _parse_json(text):
    """从 LLM 输出里抠出 JSON（容忍 ```json 围栏与前后废话）。"""
    if isinstance(text, dict):
        return text
    t = text.strip()
    t = t.replace("```json", "").replace("```", "")
    i, j = t.find("{"), t.rfind("}")
    if i >= 0 and j > i:
        return json.loads(t[i:j + 1])
    raise ValueError("LLM 未返回可解析 JSON")


class BaseOverviewLLM(object):
    """LLM 路径：把创意集 + 提示词模板交给 LLM，返回 OverviewResult。"""
    def __init__(self, llm, prompts=None, model=None):
        self.llm = llm
        self.prompts = prompts
        self.model = model
        self.id = "overview-llm"

    def summarize(self, ideas, demand=None, ctx=None):
        ideas_brief = _ideas_brief(ideas)
        if self.prompts is not None:
            try:
                prompt = self.prompts.get("synthesize", {"ideas": json.dumps(ideas_brief, ensure_ascii=False)})
            except Exception:
                prompt = self._fallback(ideas_brief)
        else:
            prompt = self._fallback(ideas_brief)
        raw = self.llm.generate(prompt, model=self.model) if self.model else self.llm.generate(prompt)
        data = _parse_json(raw)
        prov = {"model": self.model or getattr(self.llm, "id", "llm"),
                "prompt_pack": getattr(self.prompts, "id", "base")}
        return _coerce(data, getattr(demand, "id", "") if demand else "", "llm", prov)

    @staticmethod
    def _fallback(ideas_brief):
        return ("你是「汇总收敛器」。只归纳创意中实际出现的内容，不得编造，"
                "每条结论附 idea_id 溯源；若同一跨域术语出现冲突理解，显式标为 conflicts。"
                "输出 JSON：{clusters:[{label,note,idea_ids[]}], conflicts:[{term,statements:[{idea_id,claim}]}],"
                " shortlist:[{idea_id,why}], open_questions:[], warnings:[]}\n创意集：" + json.dumps(ideas_brief, ensure_ascii=False))


class AgentOverview(object):
    """Agent 路径：把整包创意（含上下文）交给另一个 Agent 读，返回 OverviewResult。"""
    def __init__(self, agent):
        self.agent = agent
        self.id = "overview-agent"

    def summarize(self, ideas, demand=None, ctx=None):
        data = self.agent.review(list(ideas), demand or None)
        prov = {"agent": getattr(self.agent, "id", "agent")}
        return _coerce(data, getattr(demand, "id", "") if demand else "", "agent", prov)
