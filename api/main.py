
# import logging
# import datetime
# from telegram import Update, Bot, Contact
# from telegram.ext import Application, CommandHandler, MessageHandler, filters
# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# import os, sqlite3, html
# from dotenv import load_dotenv
# from typing import Optional

# load_dotenv()

# # Retrieve the token and other variables from environment
# myBotToken = os.getenv("LEXI_TOKEN")
# db_name = os.getenv("DB_NAME")
# db_path = os.path.join(os.path.dirname(__file__), db_name)

# # Set up logging configuration
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

# # Cooldown duration for /everyone command (2 minutes)
# cooldown_duration = datetime.timedelta(minutes=2)
# last_use_time = None

# app = FastAPI()

# class TelegramWebhook(BaseModel):
#     update_id: int
#     message: Optional[dict]
#     edited_message: Optional[dict]
#     channel_post: Optional[dict]
#     edited_channel_post: Optional[dict]
#     inline_query: Optional[dict]
#     chosen_inline_result: Optional[dict]
#     callback_query: Optional[dict]
#     shipping_query: Optional[dict]
#     pre_checkout_query: Optional[dict]
#     poll: Optional[dict]
#     poll_answer: Optional[dict]

# def init_db():
#     try:
#         conn = sqlite3.connect(db_path)
#         c = conn.cursor()
#         c.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 user_id INTEGER PRIMARY KEY,
#                 first_name TEXT,
#                 last_name TEXT,
#                 username TEXT
#             )
#         ''')
#         conn.commit()
#     except sqlite3.Error as e:
#         logging.error(f"Database initialization error: {e}")
#     finally:
#         conn.close()

# def add_or_update_user_details(user_id, first_name, last_name, username):
#     try:
#         conn = sqlite3.connect(db_path)
#         c = conn.cursor()
#         c.execute('''
#             INSERT INTO users (user_id, first_name, last_name, username)
#             VALUES (?, ?, ?, ?)
#             ON CONFLICT(user_id) DO UPDATE SET
#                 first_name=excluded.first_name,
#                 last_name=excluded.last_name,
#                 username=excluded.username
#         ''', (user_id, first_name, last_name, username))
#         conn.commit()
#     except sqlite3.Error as e:
#         logging.error(f"Database insertion error: {e}")
#     finally:
#         conn.close()

# def get_user_ids():
#     try:
#         conn = sqlite3.connect(db_path)
#         c = conn.cursor()
#         c.execute('SELECT user_id FROM users')
#         user_ids = [row[0] for row in c.fetchall()]
#         conn.close()
#         return user_ids
#     except sqlite3.Error as e:
#         logging.error(f"Database fetch error: {e}")
#         return []

# def get_user_details(user_id):
#     try:
#         conn = sqlite3.connect(db_path)
#         c = conn.cursor()
#         c.execute('SELECT first_name, last_name, username FROM users WHERE user_id = ?', (user_id,))
#         row = c.fetchone()
#         conn.close()
#         return row
#     except sqlite3.Error as e:
#         logging.error(f"Database fetch error: {e}")
#         return None

# async def get_user_name(bot: Bot, chat_id: int, user_id: int):
#     user_details = get_user_details(user_id)
#     if user_details:
#         first_name, last_name, username = user_details
#         return first_name, last_name, username
#     return None, None, None

# async def handle_instagram_reels(update: Update, context):
#     logging.info("Received Instagram reel link.")
#     message_text = update.message.text
#     user_id = update.message.from_user.id
#     first_name = update.message.from_user.first_name
#     last_name = update.message.from_user.last_name or ""
#     username = update.message.from_user.username or ""
#     logging.info(f"User details: {user_id}, {first_name}, {last_name}, {username}")
#     add_or_update_user_details(user_id, first_name, last_name, username)
#     if "instagram.com/" in message_text:
#         expanded_url = message_text.replace("instagram.com", "ddinstagram.com")
#         await update.message.reply_text(f"Expanded Instagram Reels link: \n{expanded_url}")
#         logging.info(f"Replied with expanded URL: {expanded_url}")
#     elif "x.com/" in message_text:
#         expanded_url = message_text.replace("x.com", "fxtwitter.com")
#         await update.message.reply_text(f"Expanded Twitter link: \n{expanded_url}")
#         logging.info(f"Replied with expanded URL: {expanded_url}")

# async def mention_all(update: Update, context):
#     global last_use_time
#     current_time = datetime.datetime.now()

#     if last_use_time is None or current_time - last_use_time >= cooldown_duration:
#         last_use_time = current_time
#         chat_id = update.message.chat_id
#         bot = context.bot
#         logging.info("Executing /everyone command.")
#         try:
#             mention_message = "Attention everyone!\n\n"
#             user_ids = get_user_ids()
#             for user_id in user_ids:
#                 first_name, last_name, username = await get_user_name(bot, chat_id, int(user_id))
#                 if username:
#                     mention_message += f"[@{html.escape(username)}](tg://user?id={user_id})\n"
#                 else:
#                     full_name = f"{first_name}".strip()
#                     mention_message += f"[{full_name}](tg://user?id={user_id})\n"
#             await update.message.reply_text(mention_message, parse_mode="Markdown")
#             logging.info("Mentioned all users.")
#         except Exception as e:
#             logging.error(f"Error fetching group members: {e}")
#             await update.message.reply_text("Sorry, I couldn't fetch the list of users.")
#     else:
#         remaining_time = cooldown_duration - (current_time - last_use_time)
#         await update.message.reply_text(f"Please wait {remaining_time.seconds} seconds before using /everyone again.")

# async def fetch_user_ids_command(update: Update, context):
#     logging.info("Executing /fetch command.")
#     user_ids = get_user_ids()
#     user_details_list = []
#     for user_id in user_ids:
#         user_details = get_user_details(user_id)
#         if user_details:
#             first_name, last_name, username = user_details
#             user_details_list.append(f"{user_id} - {first_name} {last_name} (@{username})")
#     user_details_str = "\n".join(user_details_list)
#     await update.message.reply_text(f"Stored User Details:\n{user_details_str}")
#     logging.info(f"Fetched user details: {user_details_str}")

# @app.post("/webhook")
# async def webhook(request: Request):
#     webhook_data = await request.json()
#     update = Update.de_json(webhook_data, bot)
#     await application.update_queue.put(update)
#     return {"message": "ok"}

# @app.get("/")
# def index():
#     return {"message": "Hello World"}

# # Initialize the bot and application outside the request context to reuse them
# bot = Bot(token=myBotToken)
# application = Application.builder().token(myBotToken).build()

# # Add handlers to application once
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_reels))
# application.add_handler(CommandHandler("everyone", mention_all))
# application.add_handler(CommandHandler("fetch", fetch_user_ids_command))

# def main():
#     init_db()
#     logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#     print("Bot is running...")
#     application.run_polling()

# if __name__ == "__main__":
#     main()


import os
import logging
import json
from fastapi import FastAPI, Request
from api.commands import expand_instagram, expand_twitter
import re

# Retrieve the token from environment variables
TOKEN = os.getenv("LEXI_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 

app = FastAPI()

@app.get("/")
async def hello():
    return {"message":"Hello World"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        webhook_json = await request.json()  # Read request body as JSON
        chat_id = webhook_json["message"]["chat"]["id"]
        text = webhook_json["message"]["text"]
        
        logging.info(f"Received message: {text} from chat ID: {chat_id}")

        # link expand
        instagram_link = expand_instagram(chat_id,text)
        twitter_link = expand_twitter(chat_id,text)
        # if "instagram.com/" in text:
        #     expanded_url = text.replace("instagram.com", "ddinstagram.com")
        #     expanded_url = re.sub(r'\?.*igsh=.*$', '', expanded_url)
        #     logging.info(f"Here is the Expanded Link: {expanded_url}")
        #     sendMessage(chat_id,expanded_url)
        #     return {"expanded_url":expanded_url}

        return {"chat_id":chat_id,"text":text,"links":[instagram_link,twitter_link]}
    except Exception as e:
        logging.error(f"Webhook processing error: {e}")
        return {"error_message": str(e)}



# bot = Bot(token=TOKEN) 
# application = Application.builder().token(TOKEN).concurrent_updates(10).build()

# async def error_handler(update: Update, context):
    # logging.error(f"Update {update} caused error {context.error}")

# application.add_error_handler(error_handler)

# Register handlers
# async def start(update: Update, context):
    # logging.info(f"Received /start from {update.effective_chat.id}")
    # await update.message.reply_text("Hello! This is LexiBot. How can I assist you?")

# async def echo(update: Update, context):
    # await update.message.reply_text(update.message.text)

# application.add_handler(CommandHandler("start", start))
# application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# @app.on_event("startup")
# async def startup_event():
#     """Set webhook and ensure bot is initialized on startup."""
#     await application.initialize()
#     await application.start()
#     await bot.set_webhook(f"{WEBHOOK_URL}/webhook")
