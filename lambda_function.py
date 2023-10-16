from dynamo_client import DynamoClient
from customer import Customer
from order import Order
from esim_go_client import EsimGoClient
from send_email import EmailClient

def lambda_handler(event, context):
    # Extract the payload from the event
    raw_payload = event['detail']['payload']

    # Create an Order object from the payload
    order = Order(raw_payload)

    # Initialize DynamoDB, EmailClient, and EsimGoClient
    dynamo_client = DynamoClient()
    email_client = EmailClient()
    esim_client = EsimGoClient()

    # Retrieve existing customers for the given customer ID
    existing_customers = dynamo_client.get_customers(raw_payload['customer']['id'])

    # Check if multiple customers are returned for the same customer ID
    if len(existing_customers) > 1:
        print("Multiple customers returned for id: " + str(raw_payload['customer']['id']))
        return

    # Create a Customer object from the payload and order
    if len(existing_customers) == 0:
        cust = Customer.from_payload(raw_payload, order)
    else:
        cust = Customer.from_dynamo(existing_customers[0])
        cust.addOrder(order)

    # Save the new customer to DynamoDB
    put_customer_success = dynamo_client.put_customer(cust)
    if not put_customer_success:
        print("Failed to save new customer:" + str(cust))
        return

    # Save the new order to DynamoDB
    put_order_success = dynamo_client.put_order(order, cust)
    if not put_order_success:
        print("Failed to save new order:" + str(order))

    print("Order Success")

    # Generate a new eSIM order using the EsimGoClient
    esim_order_details = esim_client.new_order(order)

    if not esim_order_details:
        print("Failed to generate a new order in EsimGo:" + str(order))
        return

    print("Esim Order Success")

    # Save the eSIM order details to DynamoDB
    order_id = dynamo_client.put_esim_order(esim_order_details, order)
    if not order_id:
        print("Failed to generate a new order:" + str(esim_order_details))
        return
    else:
        print(order_id)

    print("Esim Order Updated")

    # Retrieve eSIM details using the EsimGoClient
    esim_order_details = esim_client.get_esim_details(order_id)

    if not esim_order_details:
        print("Failed to get eSIM details:" + str(esim_order_details))
        return
    else:
        # Update the eSIM order details in DynamoDB
        response = dynamo_client.update_esim_order(order_id, esim_order_details, raw_payload['line_items'])

    # Retrieve eSIM QR code images from the EsimGoClient
    image_data = esim_client.get_esim_qrcode(order_id)

    if not image_data:
        print("Failed to get eSIM details:" + str(esim_order_details))
        return
    else:
        # Update the eSIM QR code images in DynamoDB
        response = dynamo_client.update_esim_qr_code(order_id, image_data)

    print("Get Esim QR code Success")

    # Retrieve QR codes from DynamoDB
    qr_codes = dynamo_client.get_qr_code_from_db(order_id)
    if not qr_codes:
        print("Failed to get QR codes from the database:" + str(qr_codes))
        return

    # Retrieve eSIM details from DynamoDB
    esim_details = dynamo_client.get_esim_from_db(order_id)
    if not esim_details:
        print("Failed to get eSIM details from the database:" + str(esim_details))
        return

    print("Sending email to client")

    # Send an email to the client with QR codes and eSIM details
    if qr_codes:
        email_client.send_email_with_qr_code(raw_payload['contact_email'], qr_codes, esim_details, raw_payload['order_number'])
    else:
        print('QR code data not found in DynamoDB')
