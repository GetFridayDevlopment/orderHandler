import boto3
import uuid
from customer import Customer
from order import Order
from datetime import datetime
from lineitem import LineItem

def lambda_handler(event, context):
    rawPayload = event['detail']['payload']

    cust = Customer(str(uuid.uuid4()), rawPayload['customer']['id'])
    order = Order(rawPayload['id'], rawPayload['order_number'], rawPayload['total_price'])
    
    rawItems = rawPayload['line_items']
    for item in rawItems:
        order.addLineItem(LineItem(item['sku'], item['price'])) 

    client = boto3.resource('dynamodb')

    orderTable = client.Table("order")
    orderResponse = orderTable.put_item(Item={
                'id': str(uuid.uuid4()),
                'orderId':order.id,
                'shopifyOrderId': order.shopifyOrderId,
                'lineItems': order.lineItems.asdict(),
                'upsertedAt': str(datetime.now())
            })

    custTable = client.Table("customer")
    custResponse = custTable.put_item(Item={
            'id': str(uuid.uuid4()),
            'customerId':cust.customerId,
            'shopifyCustomerId':cust.shopifyCustomerId,
            'orders':[order.id],
            'upsertedAt': str(datetime.now())
        })
        
    return response