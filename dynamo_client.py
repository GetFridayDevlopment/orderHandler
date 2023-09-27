from datetime import datetime
from boto3.dynamodb.conditions import Key
import boto3


class DynamoClient:
    def __init__(self):
        client = boto3.resource('dynamodb')
        self.order_table = client.Table("order")
        self.cust_table = client.Table("customer")

    def get_customers(self, source_customer_id):
        print("source_customer_id " + str(source_customer_id))
        response = self.cust_table.query(
            IndexName='source_customer_id-index',
            KeyConditionExpression=Key(
                'source_customer_id').eq(source_customer_id),
        )
        return response['Items']

    def put_customer(self, customer):
        print(customer)
        response = self.cust_table.put_item(Item={
            'customer_id': customer.customer_id,
            'source_name': customer.souce_name,
            'source_customer_id': customer.source_customer_id,
            'orders': customer.orders,
            'upserted_at': customer.upserted_at
        })

        return response['ResponseMetadata']['HTTPStatusCode'] == 200

    def put_order(self, order, customer):
        response = self.order_table.put_item(Item={
            'orderId': order.id,
            'sourceName': order.souce_name,
            'sourceOrderId': order.source_order_id,
            'customerId': customer.customerId,
            'totalPrice': order.price,
            'orderItems': order.order_items,
            'upsertedAt': str(datetime.now())
        })

        return response['ResponseMetadata']['HTTPStatusCode'] == 200
