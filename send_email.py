import os
import json
import urllib3
from botocore.exceptions import ParamValidationError
import boto3

class EmailClient:
    def __init__(self):
        self.api_key = os.environ['SEND_GRID_API_KEY']
        self.s3_client = boto3.client('s3')
        self.s3_bucket_name = 'esim-qrcode'
    
    def send_email_with_qr_code(self, email_to, subject, qr_code_binary, esim_details):
        try:
            # Initialize an HTML email body
            print(esim_details)

            # Create an instance of urllib3 PoolManager
            http = urllib3.PoolManager()

            # Iterate through the list of image data dictionaries
            for image_data in qr_code_binary:
                image_name = image_data['image_name']
                image_url = image_data['image_url']

                try:
                    for esim in esim_details:
                        if os.path.splitext(image_name)[0] == esim['iccid']:
                            bundle = esim['bundle']
                    qr_code_url = 'https://esim-qrcode.s3.eu-west-2.amazonaws.com/' + image_name

                    with open('qr_code_email_template.html', 'r') as template_file:
                        email_template = template_file.read()

                    # Format the template with the dynamic URL
                    email_template = email_template.replace('{{bundle}}', bundle)
                    email_template = email_template.replace('{{qr_code_url}}', qr_code_url)

                    # Create the email data for SendGrid API
                    email_data = {
                        "personalizations": [
                            {
                                "to": [{"email": email_to}],
                                "subject": subject
                            }
                        ],
                        "from": {"email": "hello@easyesim.co"},
                        "content": [
                            {
                                "type": "text/html",
                                "value": email_template
                            }
                        ]
                    }

                    # Serialize email_data to JSON
                    encoded_data = json.dumps(email_data).encode('utf-8')

                    # Send the email using the SendGrid API via urllib3
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    response = http.request(
                        'POST',
                        'https://api.sendgrid.com/v3/mail/send',
                        body=encoded_data,
                        headers=headers
                    )

                    if response.status == 202:
                        print(f"Email sent successfully with status code: {response.status}")
                    else:
                        print(f"Email sending failed with status code: {response.status}")

                except ParamValidationError as e:
                    print(f"Skipping invalid image data: {str(e)}")

        except Exception as e:
            print(f"Error sending email: {str(e)}")
