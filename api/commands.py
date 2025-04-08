import logging
import re
from api.actions import sendMessage

def expand_instagram(chat_id,text):
    if "instagram.com/" in text:
        expanded_url = text.replace("instagram.com", "kkinstagram.com")
        expanded_url = re.sub(r'\?.*igsh=.*$', '', expanded_url)
        logging.info(f"Here is the Expanded Link: {expanded_url}")
        sendMessage(chat_id,expanded_url)
        return expanded_url
    
def expand_twitter(chat_id,text):
    if "x.com/" in text:
        expanded_url = text.replace("x.com", "fxtwitter.com")
        sendMessage(chat_id,expanded_url)
        logging.info(f"Replied with expanded URL: {expanded_url}")
        return expanded_url
    if "twitter.com/" in text:
        expanded_url = text.replace("twitter.com", "fxtwitter.com")
        sendMessage(chat_id,expanded_url)
        logging.info(f"Replied with expanded URL: {expanded_url}")
        return expanded_url

def mention_all(chat_id,text):
    pass
