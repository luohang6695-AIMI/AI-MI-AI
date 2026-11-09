# 无人公司跨境电商落地手册

目标：用同一套经营系统，把越南、泰国、马来西亚、新加坡、巴西、台湾的电商从“市场清单”推进到“可上线动作”。

## 1. 先把市场写进启动清单

编辑 `data/market_launch_backlog.csv`，每个国家/平台一行：

- `country`：国家代码，例如 `VN`、`TH`、`MY`、`SG`、`BR`、`TW`。
- `platform`：平台，例如 Shopee、TikTok Shop、Lazada、Mercado Livre、momo。
- `owner`：负责人，不允许空。
- `due_date`：上线/解锁日期。
- `budget_usd`：启动预算。
- `localization_status`：商品标题、详情页、素材、客服话术是否完成。
- `payment_status`：收款、结算、退款路径是否完成。
- `logistics_status`：仓、尾程、退货地址、SLA 是否完成。
- `compliance_status`：平台资质、当地法规、税务/标签/广告要求是否完成。

只有本地化、支付、物流、合规都为 `ready`，且预算不超过规则上限，系统才会给 `LAUNCH_NOW`。

## 2. 改规则，不改代码

编辑 `config/rules.json` 的 `market_launch_rules`：

- `target_countries`：要做的国家。
- `max_launch_budget_usd`：单平台启动预算上限。
- `readiness_fields`：上线前必须检查的字段。
- `required_status`：通过闸门所需状态，默认 `ready`。

## 3. 每天跑系统

```bash
python3 app/main.py --date 2026-05-22
```

系统会生成：

- `outputs/market_launch_plan_2026-05-22.md`：给人看的上线清单。
- `outputs/market_launch_plan_2026-05-22.json`：给自动化/Agent/任务系统读取的结构化动作。

## 4. 按输出执行

### LAUNCH_NOW

对 `LAUNCH_NOW` 的国家/平台，按这个顺序执行：

1. 发布店铺/商品页。
2. 开启 creator seeding 或 affiliate 招募。
3. 开启小预算广告测试。
4. 每天把 GMV、spend、ROI、库存天数写回 `data/daily_metrics.csv`。
5. 第二天继续跑 `python3 app/main.py --date YYYY-MM-DD`，让系统自动判断加预算、降预算或补货。

### BLOCKED

对 `BLOCKED` 的国家/平台，先看 blockers：

- `localization`：补本地语言标题、详情页、短视频脚本、客服话术。
- `payment`：补收款、退款、结算路径。
- `logistics`：补仓配、尾程、退货地址、履约 SLA。
- `compliance`：补平台资质、当地监管、税务、广告或标签要求。
- `budget_approval`：超过预算上限，需要 24 小时冷静期和反对者评审。

## 5. 最小可执行组织

无人公司不是没有责任，而是把责任标准化：

- `market_*`：国家负责人，负责平台上线、价格、投放预算。
- `content_*`：内容负责人，负责素材、达人、短视频脚本。
- `ops_*`：供应链/仓配负责人，负责库存、补货、退货。
- `finance`：现金流和预算门禁。
- `challenger`：反对者评审，专门阻止高风险大额动作。

## 6. 先跑哪几个市场

按当前样例输出，优先从 `LAUNCH_NOW` 市场启动：马来西亚、新加坡、泰国、台湾 Shopee、越南。巴西和台湾 momo 先清 blockers，不要硬上。

## 7. 下一步自动化

如果要继续升级，可以把 `outputs/market_launch_plan_*.json` 接到：

- 任务系统：自动派单 owner / due date。
- 广告 API：只允许 `LAUNCH_NOW` 的平台开预算。
- 店铺发布脚本：自动创建商品草稿。
- BI 看板：按国家展示 GMV、ROI、库存、现金风险。


## 8. 自动操作者怎么配合你

你负责给系统接入真实权限和数据，我负责把它变成每天可执行的操作队列：

1. 你提供平台账号/API：Shopee、Lazada、TikTok Shop、Mercado Livre、momo。
2. 你提供广告账号/API：Meta、Google、TikTok、Shopee Ads 等。
3. 你提供供应链数据：库存、采购周期、补货成本、仓库和尾程。
4. 你提供财务数据：现金流、预算上限、收款路径、审批人。
5. 系统读取 `data/operator_workflows.csv`，把 `LAUNCH_NOW`、`BLOCKED`、`REVENUE_GAP` 转换成命令。
6. 如果 `data/operator_integrations.csv` 里某个 API 还是 `missing`，命令会被阻断，状态是 `NEEDS_SETUP_OR_APPROVAL`。
7. 当集成改成 `connected` 后，命令会进入 `READY_FOR_OPERATOR`，可以交给真实执行器/API runner。

`config/rules.json` 里的 `operator_rules.monthly_min_revenue_usd` 已按 10000 万美金/月设置为 `100000000`。系统会每天计算实际 GMV 与目标 run-rate 的差距，然后生成增长冲刺命令。这个目标是经营目标，不是收益保证。
