import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

paystack_secret_key = os.getenv("PAYSTACK_SECRET_KEY")

def initialize_payment(email, amount):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "amount": amount * 100,  
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        data = response.json()
        if data.get("status"):
            url = data["data"]["authorization_url"]
            reference = data["data"]["reference"]
            return {"url": url, "reference": reference}
    return None
