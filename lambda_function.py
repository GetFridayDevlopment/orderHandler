from dynamo_client import DynamoClient
from customer import Customer
from order import Order

def lambda_handler(event, context):
    raw_payload = event['detail']['payload']
    order = Order(raw_payload)

    dynamo_client = DynamoClient()

    dynamo_client.get_customer(raw_payload['customer']['id'])

    cust = Customer(raw_payload, order)
    put_customer_success = dynamo_client.put_customer(cust, order)
    if not put_customer_success:
       print("Failed to save new customer:" + cust)

    put_order_success = dynamo_client.put_order(order, cust)
    if not put_order_success:
        print("Failed to save new order:" + order)