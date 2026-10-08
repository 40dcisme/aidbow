"""支持 `python -m aidbow_review_ui ...`。"""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
