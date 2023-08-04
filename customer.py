import uuid

class Customer:
  def __init__(self, payload, order):

    self.customerId = "C-"+str(uuid.uuid4())
    self.sourceCustomerId = payload['customer']['id']
    self.orders = [order.id]