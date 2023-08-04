from dynamo_client import DynamoClient
from customer import Customer
from order import Order

def lambda_handler(event, context):
    raw_payload = event['detail']['payload']
    order = Order(raw_payload)
    cust = Customer(raw_payload, order)

    dynamo_client = DynamoClient()
    putCustResponse = dynamo_client.put_customer(cust, order)
    print("Customer Response : ")
    print(putCustResponse)
    putOrderResponse = dynamo_client.put_order(order, cust)
    print("Order Response")
    print(putOrderResponse)