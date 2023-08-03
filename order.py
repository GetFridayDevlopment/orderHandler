import uuid

class Order:
  def __init__(self, shopifyId, number, price):
    self.id =  str(uuid.uuid4())
    self.shopifyOrderId = shopifyId
    self.orderNumber = number
    self.price = price
    self.lineItems = []

  def addLineItem(self, lineItem):
    self.lineItems.append(lineItem.asdict())

  def asdict(self):
      return {'id': self.id, 'orderNumber': self.orderNumber, 'price': self.price, 'lineItems': self.lineItems}