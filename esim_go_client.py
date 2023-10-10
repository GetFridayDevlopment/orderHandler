import urllib3
import json
from order import Order
import os
import zipfile
from PIL import Image
import io
import boto3

class EsimGoClient:
    def __init__(self):
        self.auth_key = os.environ['ESIM_GO_AUTH_KEY']
        self.s3_client = boto3.client('s3')
        self.s3_bucket_name = 'esim-qrcode'

    def new_order(self, order):
        print(order.order_items[0]['sku'])
        url = 'https://api.esim-go.com/v2.2/orders'
        payload = {
            "type": "transaction",
            "assign": True,
            "Order": [{
                "type": "bundle",
                "quantity":1,
                "item": order.order_items[0]['sku'] #Temporary
            }]
        }
        headers = {"X-API-Key": self.auth_key}
        http = urllib3.PoolManager()
        r = http.request('POST', url, body=json.dumps(payload), headers=headers)
        print(r.text)
        return r.text

    def get_esim_details(self, order_reference):
        url = "https://api.esim-go.com/v2.2/esims/assignments?reference="+order_reference
        payload={}
        headers = {"X-API-Key": self.auth_key, 'Accept': 'application/json'}
        http = urllib3.PoolManager()
        r = http.request('GET', url, fields=payload, headers=headers)
        print(r.text)
        return r.text
    
    def get_esim_qrcode(self, order_reference):
        url = "https://api.esim-go.com/v2.2/esims/assignments?reference=" + order_reference
        payload = {}
        headers = {"X-API-Key": self.auth_key, 'Accept': 'application/zip'}
        http = urllib3.PoolManager()
        response = http.request('GET', url, fields=payload, headers=headers)
        image_data_list = []  # Initialize an array to store image data

        if response.status_code == 200:
            # Create a temporary in-memory buffer to store the ZIP file content
            zip_buffer = response.content

            # Unzip the content
            with zipfile.ZipFile(io.BytesIO(zip_buffer), 'r') as zip_file:
                # Iterate through the files in the ZIP archive
                for file_info in zip_file.infolist():
                    # Check if the file has a PNG extension (you can adjust this check)
                    if file_info.filename.lower().endswith('.png'):
                        print(file_info.filename)
                        # Read the PNG image and convert it to binary
                        with zip_file.open(file_info) as png_file:
                            image_data = png_file.read()                           
                        
                        # Append image name and binary data to the image_data_list
                        

                         # Save the PNG image to S3
                        s3_object_key = file_info.filename
                        self.s3_client.put_object(Bucket=self.s3_bucket_name, Key=s3_object_key, Body=image_data)
                        
                        image_data_list.append({
                            'image_name': file_info.filename,
                            'image_url': 's3://'+self.s3_bucket_name+'/'+s3_object_key
                        })
                         # Save the image locally
                        # local_image_path = os.path.join(os.getcwd(), file_info.filename)
                        # with open(local_image_path, 'wb') as local_image_file:
                        #     local_image_file.write(binary_image)

                        
                        print(f"PNG image '{file_info.filename}' extracted from ZIP")
                    else:
                        print(f"Ignoring file '{file_info.filename}'")
           
            return image_data_list
        else:
            print(f"Failed to download ZIP file. Status code: {response.status_code}")

        return None  # Return None if the download fails