"""Read-only Shopee Open Platform sync for one shop.

Credentials are read from environment variables. This module deliberately
contains no write endpoints (price, shipment, chat, or item mutation).
"""

import argparse
import csv
import datetime as dt
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://partner.shopeemobile.com"
READ_ONLY_PATHS = frozenset({
    "/api/v2/order/get_order_list",
    "/api/v2/order/get_order_detail",
    "/api/v2/product/get_item_list",
    "/api/v2/product/get_item_base_info",
    "/api/v2/product/get_model_list",
})
TOKEN_PATH = "/api/v2/auth/access_token/get"


class ShopeeApiError(RuntimeError):
    """Raised when Shopee returns an API or transport-level error."""


class ShopeeClient:
    def __init__(self, partner_id, partner_key, shop_id, access_token, base_url=DEFAULT_BASE_URL, timeout=30, refresh_token="", token_file=None):
        self.partner_id = int(partner_id)
        self.partner_key = partner_key
        self.shop_id = int(shop_id)
        self.access_token = access_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.refresh_token = refresh_token
        self.token_file = Path(token_file) if token_file else None

    @classmethod
    def from_env(cls):
        names = ["SHOPEE_PARTNER_ID", "SHOPEE_PARTNER_KEY", "SHOPEE_SHOP_ID"]
        missing = [name for name in names if not os.environ.get(name)]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")
        token_file = Path(os.environ.get("SHOPEE_TOKEN_FILE", ROOT / "secrets" / "shopee_my_tokens.json"))
        token_data = {}
        if token_file.exists():
            token_data = json.loads(token_file.read_text(encoding="utf-8"))
        access_token = token_data.get("access_token") or os.environ.get("SHOPEE_ACCESS_TOKEN", "")
        refresh_token = token_data.get("refresh_token") or os.environ.get("SHOPEE_REFRESH_TOKEN", "")
        if not access_token or not refresh_token:
            raise SystemExit("Missing Shopee tokens: set SHOPEE_ACCESS_TOKEN and SHOPEE_REFRESH_TOKEN once, or populate SHOPEE_TOKEN_FILE")
        return cls(
            os.environ["SHOPEE_PARTNER_ID"],
            os.environ["SHOPEE_PARTNER_KEY"],
            os.environ["SHOPEE_SHOP_ID"],
            access_token,
            os.environ.get("SHOPEE_API_BASE_URL", DEFAULT_BASE_URL),
            refresh_token=refresh_token,
            token_file=token_file,
        )

    def _signature(self, path, timestamp):
        base = f"{self.partner_id}{path}{timestamp}{self.access_token}{self.shop_id}"
        return hmac.new(self.partner_key.encode(), base.encode(), hashlib.sha256).hexdigest()

    def _partner_signature(self, path, timestamp):
        base = f"{self.partner_id}{path}{timestamp}"
        return hmac.new(self.partner_key.encode(), base.encode(), hashlib.sha256).hexdigest()

    def refresh_access_token(self):
        timestamp = int(time.time())
        query = urllib.parse.urlencode({
            "partner_id": self.partner_id,
            "timestamp": timestamp,
            "sign": self._partner_signature(TOKEN_PATH, timestamp),
        })
        body = json.dumps({
            "partner_id": self.partner_id,
            "shop_id": self.shop_id,
            "refresh_token": self.refresh_token,
        }).encode()
        request = urllib.request.Request(
            f"{self.base_url}{TOKEN_PATH}?{query}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ShopeeApiError(f"Shopee token refresh failed: {exc}") from exc
        if payload.get("error"):
            raise ShopeeApiError(f"Shopee token refresh error: {payload['error']} - {payload.get('message', '')}")
        self.access_token = payload["access_token"]
        self.refresh_token = payload.get("refresh_token", self.refresh_token)
        if self.token_file:
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            self.token_file.write_text(json.dumps({
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expire_in": payload.get("expire_in"),
                "updated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            }, indent=2) + "\n", encoding="utf-8")
            os.chmod(self.token_file, 0o600)
        return payload

    def get(self, path, params=None):
        if path not in READ_ONLY_PATHS:
            raise ValueError(f"Endpoint is not allow-listed for read-only sync: {path}")
        timestamp = int(time.time())
        query = {
            "partner_id": self.partner_id,
            "timestamp": timestamp,
            "access_token": self.access_token,
            "shop_id": self.shop_id,
            "sign": self._signature(path, timestamp),
        }
        query.update(params or {})
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(query)}"
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ShopeeApiError(f"Shopee request failed for {path}: {exc}") from exc
        if payload.get("error"):
            raise ShopeeApiError(f"Shopee API error for {path}: {payload['error']} - {payload.get('message', '')}")
        return payload.get("response", {})

    def order_list(self, time_from, time_to):
        orders = []
        cursor = ""
        while True:
            response = self.get("/api/v2/order/get_order_list", {
                "time_range_field": "create_time",
                "time_from": time_from,
                "time_to": time_to,
                "page_size": 100,
                "cursor": cursor,
            })
            orders.extend(response.get("order_list", []))
            if not response.get("more"):
                return orders
            cursor = response.get("next_cursor", "")

    def order_details(self, order_sns):
        details = []
        for offset in range(0, len(order_sns), 50):
            response = self.get("/api/v2/order/get_order_detail", {
                "order_sn_list": ",".join(order_sns[offset:offset + 50]),
                "response_optional_fields": "buyer_user_id,buyer_username,item_list,total_amount,actual_shipping_fee,note,package_list",
            })
            details.extend(response.get("order_list", []))
        return details

    def item_ids(self):
        item_ids = []
        offset = 0
        while True:
            response = self.get("/api/v2/product/get_item_list", {
                "offset": offset,
                "page_size": 100,
                "item_status": "NORMAL",
            })
            item_ids.extend(item["item_id"] for item in response.get("item", []))
            if not response.get("has_next_page"):
                return item_ids
            offset = response.get("next_offset", offset + 100)

    def inventory(self):
        inventory = []
        ids = self.item_ids()
        for offset in range(0, len(ids), 50):
            batch = ids[offset:offset + 50]
            base_info = self.get("/api/v2/product/get_item_base_info", {
                "item_id_list": ",".join(map(str, batch)),
                "need_tax_info": "false",
            })
            names = {item["item_id"]: item.get("item_name", "") for item in base_info.get("item_list", [])}
            for item_id in batch:
                models = self.get("/api/v2/product/get_model_list", {"item_id": item_id}).get("model", [])
                if not models:
                    inventory.append({"item_id": item_id, "item_name": names.get(item_id, ""), "model_id": 0, "model_sku": "", "stock": 0})
                for model in models:
                    stock = sum(
                        entry.get("stock", entry.get("current_stock", 0))
                        for entry in model.get("stock_info_v2", {}).get("seller_stock", [])
                    )
                    inventory.append({
                        "item_id": item_id,
                        "item_name": names.get(item_id, ""),
                        "model_id": model.get("model_id", 0),
                        "model_sku": model.get("model_sku", ""),
                        "stock": stock,
                    })
        return inventory


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_inventory_csv(path, rows):
    fields = ["item_id", "item_name", "model_id", "model_sku", "stock"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sync(client, run_date, days, output_dir):
    client.refresh_access_token()
    end = dt.datetime.combine(run_date + dt.timedelta(days=1), dt.time.min, tzinfo=dt.timezone.utc)
    start = end - dt.timedelta(days=days)
    order_summaries = client.order_list(int(start.timestamp()), int(end.timestamp()) - 1)
    details = client.order_details([order["order_sn"] for order in order_summaries])
    inventory = client.inventory()
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = run_date.isoformat()
    write_json(output_dir / f"shopee_my_orders_{suffix}.json", order_summaries)
    write_json(output_dir / f"shopee_my_order_details_{suffix}.json", details)
    write_json(output_dir / f"shopee_my_inventory_{suffix}.json", inventory)
    write_inventory_csv(output_dir / f"shopee_my_inventory_{suffix}.csv", inventory)
    manifest = {
        "shop_id": client.shop_id,
        "synced_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "window_start_utc": start.isoformat(),
        "window_end_utc": end.isoformat(),
        "order_count": len(order_summaries),
        "order_detail_count": len(details),
        "inventory_row_count": len(inventory),
    }
    write_json(output_dir / f"shopee_my_sync_manifest_{suffix}.json", manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Read-only Shopee MY orders and inventory sync")
    parser.add_argument("--date", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--days", type=int, default=15, help="Order creation window ending after --date")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs" / "shopee")
    args = parser.parse_args()
    if not 1 <= args.days <= 15:
        parser.error("--days must be between 1 and 15")
    manifest = sync(ShopeeClient.from_env(), args.date, args.days, args.output_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
