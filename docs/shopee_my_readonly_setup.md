# 马来西亚 Shopee 单店只读接入清单

## 已实现的范围

`app/shopee_sync.py` 只允许以下 Shopee Open Platform v2 读取端点：

- `order/get_order_list`：按创建时间分页拉订单列表。
- `order/get_order_detail`：每批最多 50 个订单号拉详情。
- `product/get_item_list`：分页拉正常状态商品。
- `product/get_item_base_info`：拉商品名等基础资料。
- `product/get_model_list`：按规格拉 `stock_info_v2` 库存。

代码没有改价、发货、取消订单、回复买家、修改商品等写接口；非白名单路径会直接拒绝。

## Hang 需要申请/授权的东西

### 1. Shopee Open Platform 应用

1. Hang 使用公司主体登录 [Shopee Open Platform](https://open.shopee.com/)。
2. 注册/认证开发者，创建用于马来西亚店铺的应用。
3. 在应用审核中说明用途：单店内部 ERP，只读同步订单、订单明细、商品和库存。
4. 审核通过后取得 `partner_id` 和 `partner_key`。`partner_key` 只放密码管理器/Secret Manager，不发到聊天、不提交 Git。
5. Open Platform 控制台会显示当前应用可申请的 API 类别和权限；不同应用类型/审核状态可能不同，以控制台为准。

### 2. 回调地址

在应用控制台登记一个公司控制的 HTTPS 地址，例如：

```text
https://ops.example.com/shopee/callback
```

要求：

- 必须是公网可访问的 HTTPS 地址，且与发起授权时的 redirect 完全一致。
- 只接收 Shopee 授权返回参数；不要把 `partner_key` 放进 URL。
- 本仓库目前没有部署公网回调服务，因此这是正式授权前的外部阻塞项。

### 3. 店铺授权

1. 在 Open Platform 应用中发起 Shop Authorization，区域选择 Malaysia。
2. 用目标 Shopee MY 店铺管理员登录，在 Shopee 授权页确认授权。
3. Shopee 重定向到已登记回调地址；保存返回的授权 code。
4. 服务端用 code 换取该店的 `shop_id`、`access_token`、`refresh_token`。
5. 把 token 写入本机 `secrets/shopee_my_tokens.json`；同步任务每次运行会先刷新 token，并以 `0600` 权限更新文件。

初始 token 文件格式：

```json
{
  "access_token": "由 Hang 在安全环境填写",
  "refresh_token": "由 Hang 在安全环境填写"
}
```

### 4. 最小权限范围

只申请/启用以下读取能力（控制台名称可能略有不同）：

- Shop authorization / token refresh（授权与续期必需）。
- Order：Get Order List、Get Order Detail。
- Product：Get Item List、Get Item Base Info、Get Model List / Stock。

不要申请或不要交给本任务：更新价格、更新库存、商品编辑、发货、取消、退货决策、聊天/回复买家、财务付款等写权限。

## 凭证配置

复制 `.env.example` 的变量到公司 Secret Manager 或执行环境；不要把真实值写回 `.env.example`。

```bash
export SHOPEE_PARTNER_ID='...'
export SHOPEE_PARTNER_KEY='...'
export SHOPEE_SHOP_ID='...'
export SHOPEE_TOKEN_FILE='secrets/shopee_my_tokens.json'
```

## 首次运行与重复任务

```bash
scripts/sync_shopee_my.sh
```

默认同步截至当天 UTC 的最近 15 天创建订单，并生成：

- `outputs/shopee/shopee_my_orders_YYYY-MM-DD.json`
- `outputs/shopee/shopee_my_order_details_YYYY-MM-DD.json`
- `outputs/shopee/shopee_my_inventory_YYYY-MM-DD.json`
- `outputs/shopee/shopee_my_inventory_YYYY-MM-DD.csv`
- `outputs/shopee/shopee_my_sync_manifest_YYYY-MM-DD.json`

Cron 示例（每天 UTC 01:15；环境变量应由 Secret Manager 注入，而不是写在 crontab）：

```cron
15 1 * * * /workspace/AI-MI-AI/scripts/sync_shopee_my.sh >> /var/log/shopee-my-sync.log 2>&1
```

## 当前阻塞

仓库已经具备同步代码和离线测试，但还不能对真实店铺发请求，因为 Hang 尚未通过安全渠道提供：

- 审核通过的 `partner_id` / `partner_key`。
- 已授权店铺的 `shop_id`。
- 初始 `access_token` / `refresh_token`。
- 可用的 HTTPS 授权回调地址。
