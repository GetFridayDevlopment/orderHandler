from dynamo_client import DynamoClient
from customer import Customer
from order import Order

def lambda_handler(event, context):
    raw_payload = event['detail']['payload']
    order = Order(raw_payload)

    dynamo_client = DynamoClient()

    existing_customers = dynamo_client.get_customers(raw_payload['customer']['id'])
    if len(existing_customers) > 1:
        print("Multiple customers returned for id: " + str(raw_payload['customer']['id']))
        return

    if len(existing_customers) == 0:
        cust = Customer(raw_payload, order)
        put_customer_success = dynamo_client.put_customer(cust, order)
        if not put_customer_success:
            print("Failed to save new customer:" + cust)
            return
    else:
        cust = existing_customers[0]

    put_order_success = dynamo_client.put_order(order, cust)
    if not put_order_success:
        print("Failed to save new order:" + order)