import requests
import base64
import datetime
import os
import logging

logger = logging.getLogger(__name__)

class MpesaClient:

    def __init__(self):
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.shortcode = os.getenv('MPESA_SHORTCODE')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        self.stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    def get_access_token(self):
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        base64_bytes = base64.b64encode(auth_string.encode('ascii'))

        headers = {
            'Authorization': f'Basic {base64_bytes.decode("ascii")}'
        }

        try:
            response = requests.get(self.access_token_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            logger.error(e)
            return None

    def generate_password(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_string.encode('ascii')).decode("ascii"), timestamp


    def initiate_stk_push(self, mpesa_number, amount, account_reference='PesaCrow'):
        access_token = self.get_access_token()

        if not access_token:
            logger.error("No access token received/ Failed to get access token")
            return None

        password, timestamp = self.generate_password()
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "PartyA": mpesa_number,
            "Amount": int(amount),
            "PartyB": self.shortcode,
            "PhoneNumber": mpesa_number,
            "CallBackURL": "https://1967-217-199-148-234.ngrok-free.app/payment/mpesa/callback",
            "AccountReference": account_reference,
            "TransactionDesc": "PesaCrow"

        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(self.stk_push_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to generate stk push: {e}")
            return None





