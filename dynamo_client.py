from datetime import datetime
from boto3.dynamodb.conditions import Key
import boto3
from decimal import Decimal
import json

class DynamoClient:
    def __init__(self):
        # client = boto3.resource('dynamodb', region_name='eu-west-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        client = boto3.resource('dynamodb')
        self.order_table = client.Table("order")
        self.cust_table = client.Table("customer")
        self.esim_table = client.Table("esim_details")

    def get_customers(self, source_customer_id):
        print("source_customer_id " + str(source_customer_id))
        response = self.cust_table.query(
                IndexName='source_customer_id-index',
                KeyConditionExpression=Key('source_customer_id').eq(source_customer_id)
            )
        print(response)
        return response['Items']
        
    def put_customer(self, customer):
        response = self.cust_table.put_item(Item={
            'customer_id':customer.customer_id,
            'source_name':customer.source_name,
            'source_customer_id':customer.source_customer_id,
            'orders':customer.orders,
            'upserted_at': customer.upserted_at
        })

        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    def put_order(self, order, customer):
        response = self.order_table.put_item(Item={
                    'order_id':order.id,
                    'source_name':order.souce_name,
                    'source_order_id': order.source_order_id,
                    'customer_id': customer.customer_id,
                    'total_price': Decimal(str(order.price)),
                    'order_items': order.order_items,
                    'upserted_at': str(datetime.now())
                })
        
        return response['ResponseMetadata']['HTTPStatusCode'] == 200
    
    def put_esim_order(self, esim_order, order_table_ref):
        esim_order = json.loads(esim_order)
        print(type(esim_order))
        response = self.esim_table.put_item(Item={
                    'esim_order_id':esim_order['orderReference'],
                    'order_table_ref_id':order_table_ref.id,
                    'status':esim_order['status'],
                    'currency': esim_order['currency'],
                    'total': esim_order['total'],
                    'order':esim_order['order'],
                    'upserted_at': str(datetime.now())
                })
        
        return esim_order['orderReference']

    def update_esim_order(self, esim_order_id, new_esim_details):
        print(esim_order_id)
        # Define the update expression and attribute values for the new field
        new_esim_details = json.loads(new_esim_details)
        update_expression = "SET esim_details = :esim_details"
        expression_attribute_values = {":esim_details": new_esim_details}
        
        # Perform the update with the correct data types for the primary key
        response = self.esim_table.update_item(
            Key={'esim_order_id': esim_order_id},  # Remove the data type specifier
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

        return response

    def update_esim_qr_code(self, esim_order_id, image_data):
        print(esim_order_id)
        # Create a list to store image data
        esim_qr_codes = []

        # Iterate through the image data list and convert it to DynamoDB-friendly format
        for img in image_data:
            esim_qr_codes.append({
                "image_name":  img["image_name"],
                "image_url": img["image_url"]
            })

        # Define the update expression and attribute values for the new field
        update_expression = "SET esim_qr_codes = :esim_qr_codes"
        expression_attribute_values = {":esim_qr_codes": esim_qr_codes}

        # Perform the update
        response = self.esim_table.update_item(
            Key={'esim_order_id': esim_order_id}, 
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,  
        )

        return response

    def get_qr_code_from_db(self, esim_order_id):
        response = self.esim_table.get_item(
            Key={'esim_order_id': esim_order_id}, 
        )

        item = response.get('Item')
        if item and 'esim_qr_codes' in item:
            return item['esim_qr_codes']
    
    def get_esim_from_db(self, esim_order_id):
        response = self.esim_table.get_item(
            Key={'esim_order_id': esim_order_id}, 
        )

        item = response.get('Item')
        if item and 'esim_details' in item:
            return item['esim_details']