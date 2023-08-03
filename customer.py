import uuid

class Customer:
  def __init__(self, payload):

    self.customerId = "C-"+str(uuid.uuid4())
    self.shopifyCustomerId = payload['customer']['id']