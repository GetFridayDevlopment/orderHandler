class Order:
  def __init__(self, id, number, price):
    self.id = id
    self.orderNumber = number
    self.price = price
    self.lineItems = []

  def addLineItem(self, lineItem):
    self.lineItems.append(lineItem.asdict())

  def asdict(self):
      return {'id': self.id, 'orderNumber': self.orderNumber, 'price': self.price, 'lineItems': self.lineItems}