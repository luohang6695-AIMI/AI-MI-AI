# Autonomous Operator Queue - 2026-05-22

- Monthly minimum revenue target: $100,000,000.00
- Required daily run-rate: $3,333,333.33
- Operator mode: dry_run_until_credentials_connected

## Important
- This system does not guarantee revenue; it creates deterministic operating commands and blocks unsafe execution until integrations and approvals exist.

## Ready For Operator (0)
- No commands are executable until required integrations are connected.

## Needs Setup Or Approval (50)
- growth_operator |  |  -> `CREATE_GROWTH_SPRINT gap_usd=3260033.33 required_daily_usd=3333333.33` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | BR | Mercado Livre -> `CLEAR_LAUNCH_BLOCKERS country=BR platform=Mercado Livre blockers=logistics,compliance,budget_approval` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- finance_gatekeeper | BR | Mercado Livre -> `REQUEST_24H_COOLDOWN_AND_CHALLENGER_REVIEW country=BR platform=Mercado Livre amount_usd=12000.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | BR | Shopee -> `CLEAR_LAUNCH_BLOCKERS country=BR platform=Shopee blockers=logistics,compliance` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Shopee -> `CREATE_OR_UPDATE_STOREFRONT country=MY platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Shopee -> `PUBLISH_SKU_LIST country=MY platform=Shopee sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | MY | Shopee -> `START_CREATOR_SEEDING country=MY platform=Shopee daily_budget_usd=1750.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Shopee -> `START_AD_TEST country=MY platform=Shopee daily_budget_usd=3500.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Shopee -> `OPEN_DAILY_METRICS_LOOP country=MY platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Lazada -> `CREATE_OR_UPDATE_STOREFRONT country=MY platform=Lazada` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Lazada -> `PUBLISH_SKU_LIST country=MY platform=Lazada sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | MY | Lazada -> `START_CREATOR_SEEDING country=MY platform=Lazada daily_budget_usd=1125.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Lazada -> `START_AD_TEST country=MY platform=Lazada daily_budget_usd=2250.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | MY | Lazada -> `OPEN_DAILY_METRICS_LOOP country=MY platform=Lazada` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | Shopee -> `CREATE_OR_UPDATE_STOREFRONT country=SG platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | Shopee -> `PUBLISH_SKU_LIST country=SG platform=Shopee sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | SG | Shopee -> `START_CREATOR_SEEDING country=SG platform=Shopee daily_budget_usd=2000.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | Shopee -> `START_AD_TEST country=SG platform=Shopee daily_budget_usd=4000.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | Shopee -> `OPEN_DAILY_METRICS_LOOP country=SG platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | TikTok Shop -> `CREATE_OR_UPDATE_STOREFRONT country=SG platform=TikTok Shop` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | TikTok Shop -> `PUBLISH_SKU_LIST country=SG platform=TikTok Shop sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | SG | TikTok Shop -> `START_CREATOR_SEEDING country=SG platform=TikTok Shop daily_budget_usd=1250.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | TikTok Shop -> `START_AD_TEST country=SG platform=TikTok Shop daily_budget_usd=2500.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | SG | TikTok Shop -> `OPEN_DAILY_METRICS_LOOP country=SG platform=TikTok Shop` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Shopee -> `CREATE_OR_UPDATE_STOREFRONT country=TH platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Shopee -> `PUBLISH_SKU_LIST country=TH platform=Shopee sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | TH | Shopee -> `START_CREATOR_SEEDING country=TH platform=Shopee daily_budget_usd=1625.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Shopee -> `START_AD_TEST country=TH platform=Shopee daily_budget_usd=3250.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Shopee -> `OPEN_DAILY_METRICS_LOOP country=TH platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Lazada -> `CREATE_OR_UPDATE_STOREFRONT country=TH platform=Lazada` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Lazada -> `PUBLISH_SKU_LIST country=TH platform=Lazada sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | TH | Lazada -> `START_CREATOR_SEEDING country=TH platform=Lazada daily_budget_usd=1125.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Lazada -> `START_AD_TEST country=TH platform=Lazada daily_budget_usd=2250.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TH | Lazada -> `OPEN_DAILY_METRICS_LOOP country=TH platform=Lazada` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TW | Shopee -> `CREATE_OR_UPDATE_STOREFRONT country=TW platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TW | Shopee -> `PUBLISH_SKU_LIST country=TW platform=Shopee sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | TW | Shopee -> `START_CREATOR_SEEDING country=TW platform=Shopee daily_budget_usd=1625.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TW | Shopee -> `START_AD_TEST country=TW platform=Shopee daily_budget_usd=3250.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TW | Shopee -> `OPEN_DAILY_METRICS_LOOP country=TW platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | TW | momo -> `CLEAR_LAUNCH_BLOCKERS country=TW platform=momo blockers=payment,compliance` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | Shopee -> `CREATE_OR_UPDATE_STOREFRONT country=VN platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | Shopee -> `PUBLISH_SKU_LIST country=VN platform=Shopee sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | VN | Shopee -> `START_CREATOR_SEEDING country=VN platform=Shopee daily_budget_usd=1500.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | Shopee -> `START_AD_TEST country=VN platform=Shopee daily_budget_usd=3000.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | Shopee -> `OPEN_DAILY_METRICS_LOOP country=VN platform=Shopee` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | TikTok Shop -> `CREATE_OR_UPDATE_STOREFRONT country=VN platform=TikTok Shop` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | TikTok Shop -> `PUBLISH_SKU_LIST country=VN platform=TikTok Shop sku_bundle=core_sku` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- content_operator | VN | TikTok Shop -> `START_CREATOR_SEEDING country=VN platform=TikTok Shop daily_budget_usd=1250.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | TikTok Shop -> `START_AD_TEST country=VN platform=TikTok Shop daily_budget_usd=2500.00` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
- growth_operator | VN | TikTok Shop -> `OPEN_DAILY_METRICS_LOOP country=VN platform=TikTok Shop` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
