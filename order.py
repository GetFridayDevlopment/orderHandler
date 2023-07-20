import json

class Order:
  def __init__(self, id, number, price):
    self.id = id
    self.orderNumber = number
    self.price = price
    self.lineItems = []

  def addLineItem(self, lineItem):
    self.lineItems.append(lineItem)
    
  def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
  
  def asdict(self):
      return {'id': self.id, 'orderNumber': self.orderNumber, 'price': self.price, 'lineItems': lineItems.asdict()}