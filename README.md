# AI-MI-AI Autonomous Growth Ops MVP (Execution Upgrade)

这个版本已经把“没有负责人、没有时间、没有金额就不算安排”写进系统规则。

## 1) 直接运行

```bash
cd /workspace/AI-MI-AI
python3 app/main.py --date 2026-05-22
```

运行后会生成：
- `outputs/actions_2026-05-22.json`
- `outputs/ceo_report_2026-05-22.md`
- `outputs/cashflow_risk_2026-05-22.json`

## 2) 数据输入要求

### A. 经营数据（`data/daily_metrics.csv`）
必须包含：
- `owner`（负责人）
- `due_date`（截止时间）
- `amount_usd`（金额）

没有这三项会自动触发治理告警并阻断执行建议。

### B. 13周现金流（`data/cashflow_13_weeks.csv`）
用于识别“未来13周最低现金点”和最危险周。

## 3) 系统内置机制

- ROI低自动降预算；ROI高且库存健康自动升预算。
- 库存低于预警/危险阈值自动触发补货动作。
- 超过1万美元动作自动进入“24小时冷静期 + 反对者评审”门禁。
- CEO日报固定输出：销售、ROI、达成率、13周现金最低点。

## 4) 改规则的位置

改 `config/rules.json`：
- ROI阈值
- 库存阈值
- 审批金额阈值（默认1万美元）
