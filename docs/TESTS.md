# TESTS · 如何验证 Aidbow 跑通

> 目标：无论你是**小白**、**新 Agent**、还是**集成者**，都能用一条命令确认框架完好。

## 一、一键全跑（首选）
```bash
python3 run_all_tests.py
# 预期：各包 N passed, 0 failed；最后 ✅ ALL GREEN
```

## 二、端到端示例（看"预期成果"）
```bash
python3 examples/run_demo.py     # 预期最后一行：✅ DEMO OK
python3 examples/run_pdemo.py    # 预期最后一行：✅ P-DEMO OK
```

## 三、环境体检
```bash
python3 scripts/check_env.py     # 预期最后一行：✅ READY
```

## 四、单包测试（开发时）
```bash
python3 packages/core/run_tests.py packages/core/tests
```

## 五、作为依赖安装后测试（**可选·进阶**，与「零安装」主线无关）
```bash
pip install -e packages/core -e packages/p-system -e packages/prompts -e packages/harness
python3 -c "import aidbow_core, aidbow_p_system, aidbow_prompts, aidbow_harness; print('imports OK')"
```

## 六、CI（自动）
推分支即触发 GitHub Actions：`.github/workflows/ci.yml` 跑
`run_all_tests.py` + 两个示例（作为冒烟）。**合并前必须 CI 绿**。

## 七、判定标准（"跑通"的定义）
| 命令 | 通过标志 |
|---|---|
| `run_all_tests.py` | `✅ ALL GREEN` |
| `examples/run_demo.py` | `✅ DEMO OK` |
| `examples/run_pdemo.py` | `✅ P-DEMO OK` |
| `scripts/check_env.py` | `✅ READY` |

四条全绿 = 部署跑通、可进入二次开发。
