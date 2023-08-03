from dynamo_client import DynamoClient
from customer import Customer
from order import Order

def lambda_handler(event, context):
    raw_payload = event['detail']['payload']
    cust = Customer(raw_payload)
    order = Order(raw_payload)

    dynamo_client = DynamoClient()
    dynamo_client.put_customer(cust)
    dynamo_client.put_order(order, cust)