import requests
import json

# Set your SendGrid API key
api_key = "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"

with open('qr_code_email_template.html', 'r') as template_file:
    email_template = template_file.read()

# Define the email data with both plain text and HTML content
email_data = {
    "personalizations": [
        {
            "to": [{"email": "sivasankar.selva@gmail.com"}],
            "subject": "HTML Email Example"
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

# Send the email using the SendGrid API
url = "https://api.sendgrid.com/v3/mail/send"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, data=json.dumps(email_data))

# Check the response
if response.status_code == 202:
    print("Email sent successfully")
else:
    print(f"Email sending failed: {response.text}")
