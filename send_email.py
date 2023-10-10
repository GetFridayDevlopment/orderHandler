import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from botocore.exceptions import ParamValidationError
import urllib3
import boto3

class EmailClient:
    def __init__(self):
        # self.auth_key = os.environ['ESIM_GO_AUTH_KEY']
        self.api_key = os.environ['SEND_GRID_API_KEY']
        # self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.s3_client = boto3.client('s3')
        self.s3_bucket_name = 'esim-qrcode'
    
    def send_email_with_qr_code(self, email_to, subject, qr_code_binary, esim_details):
        try:
            sg = SendGridAPIClient(self.api_key)

            # Initialize an HTML email body
           
            print(esim_details)
            # Iterate through the list of image data dictionaries
            for image_data in qr_code_binary:
                email_body = "<html><body>"
                image_name = image_data['image_name']
                image_url = image_data['image_url']
                try:
                   for esim in esim_details:
                       if(os.path.splitext(image_name)[0] == esim['iccid']):
                           bundle = esim['bundle']
                   qr_code_url = 'https://esim-qrcode.s3.eu-west-2.amazonaws.com/'+image_name
                  
                   with open('qr_code_email_template.html', 'r') as template_file:
                    email_template = template_file.read()   
                   
                    # Format the template with the dynamic URL
                    
                    email_template = email_template.replace('{{bundle}}', bundle)
                    email_template = email_template.replace('{{qr_code_url}}', qr_code_url)

                  
                    # Create a SendGrid email message
                   message = Mail(
                        from_email='hello@easyesim.co',
                        to_emails=email_to,
                        subject=subject,
                        html_content=email_template,
                    )

                    # Send the email
                   response = sg.send(message)
                #    print(f"Email sent with status code: {response.status_code}")

                except ParamValidationError as e:
                    print(f"Skipping invalid image data: {str(e)}")

        except Exception as e:
            print(f"Error sending email: {str(e)}")