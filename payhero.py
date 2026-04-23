import requests
import json
import time
from datetime import datetime

# Configuration
CONFIG = {
    "AUTH_TOKEN": "Basic ..................",
    "ACCOUNT_ID": "0000",
    "CHANNEL_ID": 0000,
    "PROVIDER": "m-pesa",
    "CALLBACK_URL": "https://yourdomain.com/callback"
}

class PayHeroSTK:
    def __init__(self, config):
        self.config = config
        self.base_url = "https://backend.payhero.co.ke/api/v2"
    
    def _make_request(self, endpoint, method="POST", params=None, payload=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.config['AUTH_TOKEN']
        }
        
        try:
            if method == "POST":
                response = requests.post(url, headers=headers, json=payload)
            elif method == "GET":
                response = requests.get(url, headers=headers, params=params)
                
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return None

    def initiate_stk_push(self, phone_number, amount, reference, customer_name="Customer"):
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        
        payload = {
            "amount": amount,
            "phone_number": phone_number,
            "channel_id": self.config['CHANNEL_ID'],
            "provider": self.config['PROVIDER'],
            "external_reference": reference,
            "customer_name": customer_name,
            "callback_url": self.config['CALLBACK_URL'],
            "account_id": self.config['ACCOUNT_ID']
        }
        
        return self._make_request("payments", payload=payload)
    
    def check_payment_status(self, reference):
        """Check payment status using reference"""
        params = {'reference': reference}
        return self._make_request("transaction-status", method="GET", params=params)

def get_user_input():
    """Get phone number and amount from user"""
    print("\n" + "="*40)
    print("MPESA STK PUSH PAYMENT".center(40))
    print("="*40)
    
    while True:
        phone = input("\nEnter phone number (e.g., 0712345678): ").strip()
        if phone.isdigit() and len(phone) in [9, 10]:
            break
        print("Invalid phone number. Try again.")
    
    while True:
        amount = input("Enter amount (KES): ").strip()
        if amount.isdigit() and int(amount) > 0:
            break
        print("Invalid amount. Try again.")
    
    return phone, int(amount)

def process_payment():
    payhero = PayHeroSTK(CONFIG)
    
    while True:
        # Get user input
        phone, amount = get_user_input()
        reference = "PYT_" + datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Initiate payment
        print("\nSending payment request to your phone...")
        result = payhero.initiate_stk_push(phone, amount, reference)
        
        if not result or not result.get('success'):
            print("\n❌ Failed to initiate payment. Please try again.")
            continue
        
        # Check payment status
        print("\nWaiting for payment confirmation...")
        api_reference = result.get('reference')
        
        for _ in range(6):  # Check for 30 seconds (6 attempts * 5 seconds)
            time.sleep(5)
            status = payhero.check_payment_status(api_reference)
            
            if status:
                if status.get('status') == "SUCCESS":
                    print("\n✅ Payment successful!")
                    print(f"Amount: KES {amount}")
                    print(f"M-Pesa Code: {status.get('provider_reference', 'N/A')}")
                    return True
                elif status.get('status') in ["FAILED", "CANCELLED"]:
                    print("\n❌ Payment failed or was cancelled by user")
                    break
        
        # If we get here, payment wasn't completed
        choice = input("\nPayment not completed. Retry? (y/n): ").lower()
        if choice != 'y':
            return False

if __name__ == "__main__":
    process_payment()
    print("\nThank you for using our service!")
