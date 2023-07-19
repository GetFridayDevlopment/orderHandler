import boto3
import uuid
from customer import Customer
from order import Order
from datetime import datetime
from dynamodb_json import json_util as json 

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

    dynamodb_json = json.dumps(order) 
    print(dynamodb_json)

    response = table.put_item(Item={
            'id': str(uuid.uuid4()),
            'customerId':cust.customerId,
            'shopifyCustomerId':cust.shopifyCustomerId,
            'upsertedAt': str(datetime.now()),
            'orders': [order]
        })
    print(response)
    return response