"""aidbow_p_system — P 值引擎（基础版，实现 aidbow_core.PEvaluator）。"""
from .rubric import RUBRIC, P_KEYS, RUBRIC_VERSION
from .evaluator import BasePEvaluator

__all__ = ["RUBRIC", "P_KEYS", "RUBRIC_VERSION", "BasePEvaluator"]
__version__ = "0.1.0"
