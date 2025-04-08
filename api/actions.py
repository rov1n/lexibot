import requests
import os
import logging
import json

TOKEN = os.getenv("LEXI_TOKEN")
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TOKEN}'

def sendMessage(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    
    try:
        # Use `json` parameter instead of `data`
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if res.status_code != 200:
            logging.error(f"Failed to send message to user: {res.text}")
        else:
            logging.info(f"Message sent successfully: {text}")
    
    except Exception as e:
        logging.error(f"Error while sending message: {e}")
