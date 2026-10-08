"""一次跑完所有包的单测 + 集成冒烟。"""
import subprocess, sys, pathlib
root = pathlib.Path(__file__).parent
jobs = [
    ("core",     root/"packages/core"),
    ("p-system", root/"packages/p-system"),
    ("prompts",  root/"packages/prompts"),
    ("harness",  root/"packages/harness"),
    ("integration", root),
]
fail = 0
for name, wd in jobs:
    print(f"\n=== {name} ===")
    runner = wd/"run_tests.py"; tests = wd/"tests"
    if name == "integration":
        runner = root/"packages/core"/"run_tests.py"; tests = root/"tests"
    r = subprocess.run([sys.executable, str(runner), str(tests)])
    fail += r.returncode
print("\n" + ("✅ ALL GREEN" if fail == 0 else f"❌ {fail} suite(s) failed"))
sys.exit(1 if fail else 0)
