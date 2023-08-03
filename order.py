import uuid

class Order:
  def __init__(self, sourceOrderId, souceName, number, price):
    self.id =  "O-" + str(uuid.uuid4())
    self.souceName = souceName
    self.sourceOrderId = sourceOrderId
    self.sourceOrderNumber = number
    self.price = price
    self.orderItems = []

  def addOrderItem(self, lineItem):
    self.orderItems.append(lineItem.asdict())