#!/usr/bin/env python3
"""review-ui 包测试入口（与其他包一致，零三方依赖）。"""
import sys
import pathlib

PKG_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(PKG_DIR))

import unittest  # noqa: E402

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover(str(PKG_DIR / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
