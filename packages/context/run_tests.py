"""极简零依赖测试运行器：`python3 run_tests.py [tests_dir]`。也兼容 pytest。"""
import importlib.util, pathlib, sys, traceback

def _load(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def main(tests_dir=None) -> int:
    here = pathlib.Path(__file__).parent
    tdir = pathlib.Path(tests_dir) if tests_dir else here / "tests"
    fns, passed, failed = [], 0, 0
    for f in sorted(tdir.glob("test_*.py")):
        mod = _load(f)
        for name in dir(mod):
            if name.startswith("test_") and callable(getattr(mod, name)):
                fns.append((f.name, name, getattr(mod, name)))
    for fname, name, fn in fns:
        try:
            fn(); passed += 1; print(f"  \u2713 {fname}::{name}")
        except Exception:
            failed += 1; print(f"  \u2717 {fname}::{name}"); traceback.print_exc()
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
