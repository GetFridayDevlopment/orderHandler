import uuid
from datetime import datetime

class Customer:
  def __init__(self, payload, order):

    self.customer_id = "C-"+str(uuid.uuid4())
    self.source_name = "shopify"
    self.source_customer_id = payload['customer']['id']
    self.orders = [order.id]
    self.upserted_at = str(datetime.now())

  def from_dict(self, dict):
    return self.__dict__.update(dict)