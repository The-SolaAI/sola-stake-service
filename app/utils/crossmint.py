import requests
import os
from dotenv import load_dotenv

load_dotenv()

wallet = os.getenv("WALLET")
api_key = os.getenv("CROSSMINT_API")

async def create_transaction(transaction):
    url = f"https://staging.crossmint.com/api/v1-alpha2/wallets/{wallet}/transactions"
    
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "params": {
            "transaction": transaction
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
