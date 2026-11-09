# Autonomous Operator Queue - 2026-05-22

- Monthly minimum revenue target: $100,000,000.00
- Required daily run-rate: $3,333,333.33
- Operator mode: dry_run_until_credentials_connected

## Important
- This system does not guarantee revenue; it creates deterministic operating commands and blocks unsafe execution until integrations and approvals exist.

## Ready For Operator (0)
- No commands are executable until required integrations are connected.

## Needs Setup Or Approval (11)
- growth_operator |  |  -> `CREATE_GROWTH_SPRINT gap_usd=3320533.33 required_daily_usd=3333333.33` | blockers=storefront_api,ads_api,affiliate_api,inventory_api,finance_api
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
