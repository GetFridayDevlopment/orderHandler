from datetime import datetime
import boto3

class DynamoClient:
    def __init__(self):
        client = boto3.resource('dynamodb')
        self.order_table = client.Table("order")
        self.cust_table = client.Table("customer")
        
    def put_customer(self, customer, order):
        response = self.cust_table.put_item(Item={
            'customerId':customer.customerId,
            'sourceName':order.souce_name,
            'sourceCustomerId':customer.sourceCustomerId,
            'orders':customer.orders,
            'upsertedAt': str(datetime.now())
        })

        print("PUT Customer Response : " + response) 
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    def put_order(self, order, customer):
        response = self.order_table.put_item(Item={
                    'orderId':order.id,
                    'sourceName':order.souce_name,
                    'sourceOrderId': order.source_order_id,
                    'customerId': customer.customerId,
                    'totalPrice': order.price,
                    'orderItems': order.order_items,
                    'upsertedAt': str(datetime.now())
                })
        
        print("PUT Order Response : " + response)
        return response['ResponseMetadata']['HTTPStatusCode'] == 200

