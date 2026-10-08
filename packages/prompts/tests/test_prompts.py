import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "core"))
from aidbow_core import PromptPack
from aidbow_prompts import BasePromptPack

def test_implements_promptpack():
    assert isinstance(BasePromptPack(), PromptPack)

def test_get_with_vars():
    pk = BasePromptPack()
    out = pk.get("decompose", {"prompt": "做宣发", "constraints": "无预算", "context": "-"})
    assert "做宣发" in out and "无预算" in out

def test_overlay_precedence():
    d = tempfile.mkdtemp()
    open(os.path.join(d, "decompose.txt"), "w", encoding="utf-8").write("CUSTOM {{prompt}}")
    pk = BasePromptPack(overlay_dir=d)
    assert pk.get("decompose", {"prompt": "X"}) == "CUSTOM X"

def test_templates_contain_anti_hallucination():
    pk = BasePromptPack()
    assert "编造" in pk.get("synthesize")           # 汇总含抗幻觉
    assert "冲突" in pk.get("synthesize")           # 含跨专业冲突标记
