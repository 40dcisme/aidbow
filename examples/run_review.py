#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""评审台示例：用内置 demo 数据生成一个自包含评审页（离线，零配置）。

    python3 examples/run_review.py            # 输出 ./review_demo.html
    python3 examples/run_review.py -o out.html
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG = os.path.join(os.path.dirname(_HERE), "packages")
for _p in ["core", "review-ui"]:
    sys.path.insert(0, os.path.join(_PKG, _p))

# 优先用包自带示例数据；缺失则用内置最小样例
_DEMO = os.path.join(_PKG, "review-ui", "examples", "ideas.demo.json")


def main():
    ap = argparse.ArgumentParser(description="生成 aidbow 评审台示例页（自包含 HTML）")
    ap.add_argument("-o", "--out", default="review_demo.html")
    args = ap.parse_args()

    from aidbow_review_ui import load_ideas, write_page
    import json

    if os.path.exists(_DEMO):
        raw = json.load(open(_DEMO, encoding="utf-8"))
        ideas = load_ideas(raw if isinstance(raw, list) else raw.get("ideas", []))
        demand_id = raw.get("demandId", "demo-001") if isinstance(raw, dict) else "demo-001"
    else:
        ideas = load_ideas([
            {"id": "A:01", "author": "anon", "round": "R1", "title": "示例创意",
             "oneLiner": "一句话核心", "body": "**正文**：示例内容" * 10,
             "P": {"P1": 4, "P2": 4, "P3": 3, "P4": 3, "P5": 4, "P6": 4, "P7": 4}},
        ])
        demand_id = "demo-001"

    write_page(ideas, demand_id, args.out)
    print("OK 生成 %s（%d 条创意，自包含 HTML，可直接用浏览器打开）" % (args.out, len(ideas)))


if __name__ == "__main__":
    main()
