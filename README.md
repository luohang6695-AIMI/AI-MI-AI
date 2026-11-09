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
- `outputs/market_launch_plan_2026-05-22.json`
- `outputs/market_launch_plan_2026-05-22.md`
- `outputs/operator_queue_2026-05-22.json`
- `outputs/operator_queue_2026-05-22.md`

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
- 跨境电商启动台覆盖越南、泰国、马来西亚、新加坡、巴西、台湾；按本地化、支付、物流、合规和预算闸门自动判断 `LAUNCH_NOW` 或 `BLOCKED`。

## 4) 跨境电商启动台

新增 `data/market_launch_backlog.csv` 作为无人公司市场启动清单。每一行必须定义：

- `country` / `platform`：国家与电商平台。
- `owner` / `due_date` / `budget_usd`：无人公司仍然需要责任人、时间和金额。
- `localization_status` / `payment_status` / `logistics_status` / `compliance_status`：全部为 `ready` 才能启动。

当前内置启动范围：

- 越南：Shopee、TikTok Shop
- 泰国：Shopee、Lazada
- 马来西亚：Shopee、Lazada
- 新加坡：Shopee、TikTok Shop
- 巴西：Mercado Livre、Shopee
- 台湾：Shopee、momo

## 5) 改规则的位置

改 `config/rules.json`：
- ROI阈值
- 库存阈值
- 审批金额阈值（默认1万美元）
- 跨境启动国家、预算上限和 readiness 字段

## 6) 具体落地步骤

如果你要“直接把越南、泰国、马来西亚、新加坡、巴西、台湾的电商做出来”，按这个顺序做：

1. 在 `data/market_launch_backlog.csv` 填国家、平台、负责人、上线日期、预算和四个 readiness 状态。
2. 在 `config/rules.json` 调整 `market_launch_rules`，决定目标国家、预算上限和上线闸门。
3. 运行 `python3 app/main.py --date YYYY-MM-DD`。
4. 打开 `outputs/market_launch_plan_YYYY-MM-DD.md`。
5. 对 `LAUNCH_NOW` 直接发布店铺/商品、启动达人和小预算广告。
6. 对 `BLOCKED` 先清理 blockers，不能跳过支付、物流、合规和预算闸门。
7. 每天把 GMV、广告花费、ROI、库存天数写回 `data/daily_metrics.csv`，再跑系统，让它自动给出加预算、降预算、补货和审批动作。

更完整的操作手册见 `docs/unmanned_ecommerce_playbook.md`。

## 7) 自动操作者系统

新增自动操作者队列：

- `data/operator_workflows.csv` 定义系统可以自动发出的操作命令，例如建店、发布 SKU、达人种草、广告测试、增长冲刺。
- `data/operator_integrations.csv` 定义真实自动化所需 API 接入状态。没有接入平台、广告、达人、库存、财务 API 时，系统只会进入 `NEEDS_SETUP_OR_APPROVAL`，不会假装已经执行。
- `config/rules.json` 的 `operator_rules.monthly_min_revenue_usd` 默认设置为 `100000000`，对应你说的每月至少 10000 万美金目标；系统会换算成每日 run-rate，并生成增长缺口命令。
- `outputs/operator_queue_YYYY-MM-DD.md` 是我作为操作者每天要执行/推进的命令清单。

注意：程序可以自动化操作流程、预算闸门和任务派发，但不能保证收入结果；10000 万美金/月必须靠产品、供应链、流量、资金和合规共同达成。

## 8) 马来西亚益生菌爆品战役

新增 `data/growth_campaigns.csv`，用于把“我要把益生菌打爆”转换成可执行预算与运营动作。当前样例为 MY Shopee：

- 预算拆分：35% Shopee Ads，65% Coins。
- Shopee Ads 覆盖 Product Ads、Shop Ads、Live Ads。
- Coins 必须配合直播和 Shopee Ads，不单独烧。
- 老板娘/核心主播直播目标在线人数不少于 3,000。
- 输出文件：`outputs/growth_campaign_plan_YYYY-MM-DD.md` 与 `.json`。

安全要求：不要把平台密码、手机号验证码、个人账号密码写进仓库；只在密码管理器或平台子账号权限中管理。

## 9) 先从马来西亚开始

可以只跑马来西亚，不影响其他国家数据：

```bash
python3 app/main.py --date 2026-05-22 --country MY
```

系统会生成带国家后缀的文件，例如：

- `outputs/actions_2026-05-22_MY.json`
- `outputs/market_launch_plan_2026-05-22_MY.md`
- `outputs/operator_queue_2026-05-22_MY.md`
- `outputs/growth_campaign_plan_2026-05-22_MY.md`

账号密码不要写进仓库；请放到密码管理器或 `secrets/` 目录（该目录已被 `.gitignore` 忽略）。

## 10) 你不会操作也没关系

你只需要把资料按 `data/malaysia_operator_intake.csv` 给齐，我来操作系统：

- 平台权限用子账号、密码管理器或 API token，不要在聊天里发密码。
- 产品、库存、预算、素材、合规资料用表格/云盘给。
- 运行 `python3 app/main.py --date 2026-05-22 --country MY` 会生成 `outputs/operator_intake_2026-05-22_MY.md`，里面只列缺什么资料。
- 我根据 intake checklist 补齐系统输入，再执行 operator queue。

## 11) Shopee MY 单店只读同步

订单列表、订单详情和商品库存的只读同步任务已经放在 `app/shopee_sync.py`；完整申请、授权、回调、最小权限和定时任务清单见 `docs/shopee_my_readonly_setup.md`。

```bash
scripts/sync_shopee_my.sh
```

任务只允许读取白名单端点，不包含改价、发货、取消订单、回复买家或修改商品等写操作。真实店同步需要 Hang 先完成 Shopee Open Platform 应用审核、店铺授权，并通过安全渠道配置 partner/shop/token 凭证。
