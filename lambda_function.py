from dynamo_client import DynamoClient
from customer import Customer
from order import Order
from esim_go_client import EsimGoClient
from send_email import EmailClient

def lambda_handler(event, context):
    raw_payload = event['detail']['payload']
    order = Order(raw_payload)
    order1 = Order(raw_payload)
    dynamo_client = DynamoClient()
    email_client = EmailClient()
    print(raw_payload['order_number'])
    existing_customers = dynamo_client.get_customers(raw_payload['customer']['id'])
    
    if len(existing_customers) > 1:
        print("Multiple customers returned for id: " + str(raw_payload['customer']['id']))
        return
    if len(existing_customers) == 0:
        cust = Customer.from_payload(raw_payload, order)
    else:
        cust = Customer.from_dynamo(existing_customers[0])
        cust.addOrder(order)

    put_customer_success = dynamo_client.put_customer(cust)
    if not put_customer_success:
        print("Failed to save new customer:" + cust)
        return

    put_order_success = dynamo_client.put_order(order, cust)
    if not put_order_success:
        print("Failed to save new order:" + order)
    
    print(order)
    esim_client = EsimGoClient()
    esim_order_details = esim_client.new_order(order1)

    if not esim_order_details:
        print("Failed to generate new order in esimGo:" + str(order1))
        return
    

    order_id = dynamo_client.put_esim_order(esim_order_details, order1)
    if not order_id:
        print("Failed to generate new order:" + esim_order_details)
        return
    else:
        print(order_id)

  
    esim_order_details = esim_client.get_esim_details(order_id)

    if not esim_order_details:
        print("Failed to get esim details:" + esim_order_details)
        return
    else:
        response = dynamo_client.update_esim_order(order_id, esim_order_details)
    
    image_data = esim_client.get_esim_qrcode(order_id)

    if not image_data:
        print("Failed to get esim details:" + esim_order_details)
        return
    else:
        response = dynamo_client.update_esim_qr_code(order_id, image_data)
    
    
    qr_codes = dynamo_client.get_qr_code_from_db(order_id)
    if not qr_codes:
        print("Failed to get qr code from db :" + qr_codes)
        return
    

    esim_details = dynamo_client.get_esim_from_db(order_id)
    if not esim_details:
        print("Failed to get esim_details from db :" + esim_details)
        return
  

    if qr_codes:
        email_client.send_email_with_qr_code(raw_payload['contact_email'], 'QR Code Email', qr_codes, esim_details)
    else:
        print('QR code data not found in DynamoDB')