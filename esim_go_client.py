import urllib3
import json
from order import Order
import os


class EsimGoClient:
    def __init__(self) -> None:
        self.auth_key = os.environ['ESIM_GO_AUTH_KEY']
        pass

    def new_order(self, order: Order):
        http = urllib3.PoolManager()
        url = 'https://api.esim-go.com/v2.2/orders'
        payload = {
            "type": "validate",
            "assign": "true",
            "Order": [{
                "type": "bundle",
                "quantity": 1,
                "item": order.order_items[0].sku  # Temporary
            }]
        }
        headers = {"X-API-Key": self.auth_key}

        r = http.request('POST', url, body=json.dumps(
            payload), headers=headers)
        print(r.content)
