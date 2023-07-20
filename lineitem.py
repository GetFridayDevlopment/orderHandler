class LineItem:
  def __init__(self, sku, price):
    self.sku = sku
    self.price = price

  def asdict(self):
      return {'sku': self.sku, 'price': self.price}