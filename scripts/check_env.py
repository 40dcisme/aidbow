#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""环境自检 —— 新 Agent / 小白部署后的第一道体检。

     python3 scripts/check_env.py

逐项检查并给出修复提示；全部通过时最后打印 ✅ READY。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKGS = ["core", "p-system", "prompts", "harness", "adapters", "context", "review-ui"]
for p in PKGS:
    sys.path.insert(0, os.path.join(ROOT, "packages", p))

fails = []

def ok(msg):
    print("  [OK]  " + msg)

def fail(msg, hint=""):
    print("  [FAIL] " + msg + (("  → " + hint) if hint else ""))
    fails.append(msg)

print("=" * 58)
print("Aidbow 环境自检")
print("=" * 58)

# 1) Python 版本
v = sys.version_info
print("\n1) Python 版本：%d.%d.%d" % (v.major, v.minor, v.micro))
if v >= (3, 9):
    ok("Python >= 3.9")
else:
    fail("需要 Python >= 3.9", "升级 Python 后重试")

# 2) 关键文件在位
print("\n2) 仓库文件")
for rel in ["SPEC.md", "run_all_tests.py", "examples/run_demo.py"]:
    if os.path.exists(os.path.join(ROOT, rel)):
        ok(rel)
    else:
        fail("缺少 " + rel, "请在仓库根目录运行本脚本")

# 3) 关键包可导入
print("\n3) 包导入")
for mod in ["aidbow_core", "aidbow_p_system", "aidbow_prompts", "aidbow_harness"]:
    try:
        __import__(mod); ok("import " + mod)
    except Exception as e:
        fail("import %s 失败：%s" % (mod, e), "检查 packages/*/ 是否完整")

# 4) 最小端到端可跑
print("\n4) 端到端冒烟")
try:
    from aidbow_core import Demand, Idea
    from aidbow_p_system import BasePEvaluator
    ev = BasePEvaluator()
    res = ev.evaluate(Idea(id="a:1", author="x", round="R1", title="t", oneLiner="o",
                           body="**正文**：" + "字" * 450, P={"P2": 4}),
                      Demand(id="d1", prompt="p"))
    assert "P3" in res.P
    ok("P 引擎可用（P3=%s）" % res.P.get("P3"))
except Exception as e:
    fail("端到端冒烟失败：%s" % e, "见 QUICKSTART §9 常见问题")

# 5) 可选能力（缺了不算失败）
print("\n5) 可选能力")
try:
    __import__("aidbow_adapters"); ok("adapters 可导入（真实 LLM 接入用）")
except Exception:
    print("  [--]  adapters 未就绪（不影响离线跑通）")
try:
    __import__("aidbow_review_ui"); ok("review-ui 可导入（可视化评审台）")
except Exception:
    print("  [--]  review-ui 未就绪（不影响离线跑通）")

print("\n" + "=" * 58)
if fails:
    print("❌ %d 项未通过，请按上方提示修复后重试。" % len(fails))
    sys.exit(1)
print("✅ READY")
