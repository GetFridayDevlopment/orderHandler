import boto3
import uuid
from customer import Customer
from order import Order
from datetime import datetime
import json

def lambda_handler(event, context):
    # this will create dynamodb resource object and
    # here dynamodb is resource name
    client = boto3.resource('dynamodb')

    # this will search for dynamoDB table
    # your table name may be different
    table = client.Table("customer")
    print(table.table_status)

    rawPayload = event['detail']['payload']

    cust = Customer(str(uuid.uuid4()), rawPayload['customer']['id'])

    order = Order(rawPayload['id'], rawPayload['order_number'], rawPayload['total_price'])

    print(event)

    response = table.put_item(Item={
            'id': str(uuid.uuid4()),
            'customerId':cust.customerId,
            'shopifyCustomerId':cust.shopifyCustomerId,
            'upsertedAt': str(datetime.now())
        })
    print(response)
    return response