import urllib3
import json
from order import Order
import os
import zipfile
import io
import boto3
import logging
import time 

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class EsimGoClient:
    def __init__(self):
        self.auth_key = os.environ['ESIM_GO_AUTH_KEY']
        self.s3_client = boto3.client('s3')
        self.s3_bucket_name = 'esim-qrcode'

    def new_order(self, order):
        url = 'https://api.esim-go.com/v2.3/orders'
        order_items_payload = []

        for order_item in order.order_items:
            item_payload = {
                "type": "bundle",
                "quantity": order_item['qty'],
                "item": order_item['sku']
            }
            order_items_payload.append(item_payload)

        payload = {
            "type": "transaction",
            "assign": True,
            "Order": order_items_payload
        }
        headers = {"X-API-Key": self.auth_key}
        http = urllib3.PoolManager()
        
        for attempt in range(3):
            try:
                r = http.request('POST', url, body=json.dumps(payload), headers=headers)
                response_text = r.data.decode('utf-8')
                logger.info("New order response: %s", response_text)
                 # Check for 503 status code
                if r.status == 503:
                    logger.info("Received 503 status code. Adding delay before retrying...")
                    time.sleep(5)  # Add a delay of 5 seconds (adjust as needed)
                    
                return response_text
            except Exception as e:
                logger.error("Attempt %d: Failed to create new order: %s", attempt + 1, str(e))
                if attempt < 2:
                    logger.info("Retrying...")
                    time.sleep(5)  # Add a delay before retrying (adjust as needed)
                else:
                    raise

    def get_esim_details(self, order_reference):
        url = "https://api.esim-go.com/v2.3/esims/assignments?reference=" + order_reference
        payload = {}
        headers = {"X-API-Key": self.auth_key, 'Accept': 'application/json'}
        http = urllib3.PoolManager()

        for attempt in range(3):
            try:
                r = http.request('GET', url, fields=payload, headers=headers)
                response_text = r.data.decode('utf-8')
                logger.info("Get eSIM details response: %s", response_text)
                 # Check for 500 status code or empty response
                if r.status == 500 or not response_text:
                    logger.info("Received 500 status code or empty response. Retrying...")
                    time.sleep(5)  # Add a delay of 5 seconds (adjust as needed)
                    continue
                
                return response_text
            except Exception as e:
                logger.error("Attempt %d: Failed to get eSIM details: %s", attempt + 1, str(e))
                if attempt < 2:
                    logger.info("Retrying...")
                    time.sleep(5)  # Add a delay before retrying (adjust as needed)
                else:
                    raise

    def get_esim_qrcode(self, order_reference):
        url = "https://api.esim-go.com/v2.3/esims/assignments?reference=" + order_reference
        payload = {}
        headers = {"X-API-Key": self.auth_key, 'Accept': 'application/zip'}
        http = urllib3.PoolManager()

        for attempt in range(3):
            try:
                response = http.request('GET', url, fields=payload, headers=headers)
                 # Check for 500 status code or empty response
                if response.status == 500 or not response.data:
                    logger.info("Received 500 status code or empty response. Retrying...")
                    time.sleep(5)  # Add a delay of 5 seconds (adjust as needed)
                    continue
                
                if response.status == 200:
                    zip_buffer = response.data
                    image_data_list = []
                    with zipfile.ZipFile(io.BytesIO(zip_buffer), 'r') as zip_file:
                        for file_info in zip_file.infolist():
                            if file_info.filename.lower().endswith('.png'):
                                with zip_file.open(file_info) as png_file:
                                    image_data = png_file.read()
                                s3_object_key = file_info.filename
                                self.s3_client.put_object(Bucket=self.s3_bucket_name, Key=s3_object_key, Body=image_data)
                                image_data_list.append({
                                    'image_name': file_info.filename,
                                    'image_url': 's3://' + self.s3_bucket_name + '/' + s3_object_key
                                })
                                logger.info("PNG image '%s' extracted from ZIP", file_info.filename)
                            else:
                                logger.info("Ignoring file '%s'", file_info.filename)
                    return image_data_list
                else:
                    logger.error("Failed to download ZIP file. Status code: %s", response.status)
            except Exception as e:
                logger.error("Attempt %d: Failed to get eSIM QR code: %s", attempt + 1, str(e))
                if attempt < 2:
                    logger.info("Retrying...")
                    time.sleep(5)
                else:
                    raise

        return None
