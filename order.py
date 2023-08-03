import uuid

class Order:
  def __init__(self, sourceOrderId, souceName, number, price):
    self.id =  str(uuid.uuid4())
    self.souceName = souceName
    self.sourceOrderId = sourceId
    self.sourceOrderNumber = number
    self.price = price
    self.orderItems = []

  def addOrderItem(self, lineItem):
    self.orderItems.append(lineItem.asdict())

  def asdict(self):
      return {'id': self.id, 'orderNumber': self.orderNumber, 'price': self.price, 'lineItems': self.lineItems}