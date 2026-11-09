import hashlib
import hmac
import tempfile
import unittest
from datetime import date
from pathlib import Path

from app.shopee_sync import READ_ONLY_PATHS, ShopeeClient, sync


class FakeClient:
    shop_id = 123

    def refresh_access_token(self):
        return {"access_token": "refreshed"}

    def order_list(self, time_from, time_to):
        return [{"order_sn": "ORDER-1"}]

    def order_details(self, order_sns):
        return [{"order_sn": order_sns[0], "item_list": []}]

    def inventory(self):
        return [{"item_id": 1, "item_name": "Probiotic", "model_id": 2, "model_sku": "PB-1", "stock": 10}]


class ShopeeClientTests(unittest.TestCase):
    def test_shop_signature(self):
        client = ShopeeClient(1001, "secret", 2002, "token")
        path = "/api/v2/order/get_order_list"
        expected_base = "1001/api/v2/order/get_order_list1700000000token2002"
        expected = hmac.new(b"secret", expected_base.encode(), hashlib.sha256).hexdigest()
        self.assertEqual(client._signature(path, 1700000000), expected)

    def test_rejects_non_read_only_endpoint(self):
        client = ShopeeClient(1, "secret", 2, "token")
        self.assertNotIn("/api/v2/product/update_price", READ_ONLY_PATHS)
        with self.assertRaises(ValueError):
            client.get("/api/v2/product/update_price", {})

    def test_sync_writes_repeatable_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            manifest = sync(FakeClient(), date(2026, 11, 8), 1, output)
            self.assertEqual(manifest["order_count"], 1)
            self.assertTrue((output / "shopee_my_orders_2026-11-08.json").exists())
            self.assertTrue((output / "shopee_my_order_details_2026-11-08.json").exists())
            self.assertTrue((output / "shopee_my_inventory_2026-11-08.csv").exists())


if __name__ == "__main__":
    unittest.main()
