from dynamo_client import DynamoClient
from customer import Customer
from order import Order
from esim_go_client import EsimGoClient

def lambda_handler(event, context):
    raw_payload = event['detail']['payload']
    order = Order(raw_payload)

    dynamo_client = DynamoClient()

    existing_customers = dynamo_client.get_customers(raw_payload['customer']['id'])
    
    if len(existing_customers) > 1:
        print("Multiple customers returned for id: " + str(raw_payload['customer']['id']))
        return
    if len(existing_customers) == 0:
        cust = Customer.from_payload(raw_payload, order)
    else:
        cust = Customer.from_dynamo(existing_customers[0])
        cust.addOrder(order)

    put_customer_success = dynamo_client.put_customer(cust)
    if not put_customer_success:
        print("Failed to save new customer:" + cust)
        return

    put_order_success = dynamo_client.put_order(order, cust)
    if not put_order_success:
        print("Failed to save new order:" + order)

    esim_client = EsimGoClient()
    esim_client.new_order(order)