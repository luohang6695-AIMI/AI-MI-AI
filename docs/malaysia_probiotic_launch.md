# 马来西亚益生菌爆品战役

目标：把马来西亚 Shopee 作为第一战场，围绕益生菌 Hero SKU 建立“直播 + Shopee Ads + Coins + Affiliate + 日报复盘”的增长闭环。

## 1. 安全交接原则

交接资料里包含平台账号、密码、OTP 手机号和个人邮箱。这些信息不能写进代码仓库，也不能放进 CSV 明文文件。

正确做法：

1. 把所有密码迁移到密码管理器。
2. 为运营、广告、仓库、财务分别开平台子账号。
3. 能用 API token 就不要共享主账号密码。
4. 所有 OTP 绑定到公司设备或公司手机号。
5. 离职/换岗后立即轮换密码和 token。

## 2. 马来西亚现有运营资产

已知可运营渠道：

- Shopee：品牌店、affiliate 账号、直播/金币/站内广告。
- TikTok / TikTok Shop：内容、达人、店铺成交。
- Lazada：补充销售平台。
- Instagram / XHS：内容种草与素材复用。
- DHL / ShopeeXpress：履约与补发。
- Google Sheets：销售表、库存表、客服补发、直播机制、日报。

## 3. 益生菌打爆打法

### 3.1 预算拆分

默认写入 `data/growth_campaigns.csv`：

- 35%：Shopee Ads，包括 Product Ads、Shop Ads、Live Ads。
- 65%：Coins，用于直播间拉在线和转化。

Coins 不单独烧，必须配合直播和 Shopee Ads。

### 3.2 直播在线目标

普通主播：按预算档位拉在线人数。

核心主播/老板娘场：在线人数必须至少 3,000，并向 6,000 冲刺。

### 3.3 每日执行节奏

1. 上午：检查库存、昨日 GMV、ROI、退款率、客服补发。
2. 中午：确定直播 SKU、赠品、秒杀、Coins 预算。
3. 下午：开 Product Ads / Shop Ads / Live Ads。
4. 晚上：直播冲刺，Coins 配合投放，不允许无直播空烧。
5. 23:59 前：日报同步完成事项、未完成事项、发现、建议和下周计划。

## 4. 系统如何接管

1. 在 `data/growth_campaigns.csv` 填益生菌 Campaign。
2. 运行 `python3 app/main.py --date YYYY-MM-DD`。
3. 查看 `outputs/growth_campaign_plan_YYYY-MM-DD.md`。
4. 如果库存、合规、ROI、现金流没触发 kill switch，就执行预算和直播动作。
5. 每天把结果写回 `data/daily_metrics.csv`，让系统判断继续放量、降预算或补货。

## 5. Kill Switch

以下情况必须停或降：

- 库存天数低于预警线。
- ROI 低于系统低 ROI 阈值。
- 退款率或客服补发异常上升。
- 益生菌功效宣称产生合规风险。
- 现金流或预算审批未通过。
