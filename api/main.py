
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
from typing import Optional

from fastapi import FastAPI, Request
from pydantic import BaseModel

from telegram import Update, Bot
from telegram.ext import Dispatcher, MessageHandler, Filters, CommandHandler

TOKEN = os.environ.get("LEXI_TOKEN")

app = FastAPI()

class TelegramWebhook(BaseModel):
    '''
    Telegram Webhook Model using Pydantic for request body validation
    '''
    update_id: int
    message: Optional[dict]
    edited_message: Optional[dict]
    channel_post: Optional[dict]
    edited_channel_post: Optional[dict]
    inline_query: Optional[dict]
    chosen_inline_result: Optional[dict]
    callback_query: Optional[dict]
    shipping_query: Optional[dict]
    pre_checkout_query: Optional[dict]
    poll: Optional[dict]
    poll_answer: Optional[dict]

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def register_handlers(dispatcher):
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

@app.post("/webhook")
def webhook(webhook_data: TelegramWebhook):
    '''
    Telegram Webhook
    '''
    # Method 1
    bot = Bot(token=TOKEN)
    update = Update.de_json(webhook_data.__dict__, bot) # convert the Telegram Webhook class to dictionary using __dict__ dunder method
    dispatcher = Dispatcher(bot, None, workers=4)
    register_handlers(dispatcher)

    # handle webhook request
    dispatcher.process_update(update)

    # Method 2
    # you can just handle the webhook request here without using python-telegram-bot
    # if webhook_data.message:
    #     if webhook_data.message.text == '/start':
    #         send_message(webhook_data.message.chat.id, 'Hello World')

    return {"message": "ok"}

@app.get("/")
def index():
    return {"message": "Hello World"}