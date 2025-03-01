import logging
import datetime
from telegram import Update, Bot, Contact
from telegram.ext import Application, CommandHandler, MessageHandler, filters, Dispatcher
from fastapi import FastAPI, Request
from pydantic import BaseModel
# import config  # Import config file
import os, sqlite3, html
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# Retrieve the token and other variables from environment
myBotToken = os.getenv("LEXI_TOKEN")
db_name = os.getenv("DB_NAME")
db_path = os.path.join(os.path.dirname(__file__), db_name)

# Cooldown duration for /everyone command (2 minutes)
cooldown_duration = datetime.timedelta(minutes=2)
last_use_time = None

app = FastAPI()

class TelegramWebhook(BaseModel):
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

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_or_update_user_details(user_id, first_name, last_name, username):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (user_id, first_name, last_name, username)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            first_name=excluded.first_name,
            last_name=excluded.last_name,
            username=excluded.username
    ''', (user_id, first_name, last_name, username))
    conn.commit()
    conn.close()

def get_user_ids():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return user_ids

def get_user_details(user_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT first_name, last_name, username FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

async def get_user_name(bot: Bot, chat_id: int, user_id: int):
    user_details = get_user_details(user_id)
    if user_details:
        first_name, last_name, username = user_details
        return first_name, last_name, username
    return None, None, None

async def get_user_details_from_api(bot, user_id):
    user = await bot.get_chat(user_id)
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username
    }

async def handle_instagram_reels(update: Update, context):
    message_text = update.message.text
    user_id = update.message.from_user.id
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name or ""
    username = update.message.from_user.username or ""
    add_or_update_user_details(user_id, first_name, last_name, username)
    if "instagram.com/" in message_text:
        expanded_url = message_text.replace("instagram.com", "ddinstagram.com")
        await update.message.reply_text(f"Expanded Instagram Reels link: \n{expanded_url}")
    elif "x.com/" in message_text:
        expanded_url = message_text.replace("x.com", "fxtwitter.com")
        await update.message.reply_text(f"Expanded Twitter link: \n{expanded_url}")

async def mention_all(update: Update, context):
    global last_use_time
    current_time = datetime.datetime.now()

    if last_use_time is None or current_time - last_use_time >= cooldown_duration:
        last_use_time = current_time
        chat_id = update.message.chat_id
        bot = context.bot
        try:
            mention_message = "Attention everyone!\n\n"
            user_ids = get_user_ids()
            for user_id in user_ids:
                first_name, last_name, username = await get_user_name(bot, chat_id, int(user_id))
                if username:
                    mention_message += f"[@{html.escape(username)}](tg://user?id={user_id})\n"
                else:
                    full_name = f"{first_name}".strip()
                    mention_message += f"[{full_name}](tg://user?id={user_id})\n"
            await update.message.reply_text(mention_message, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error fetching group members: {e}")
            await update.message.reply_text("Sorry, I couldn't fetch the list of users.")
    else:
        remaining_time = cooldown_duration - (current_time - last_use_time)
        await update.message.reply_text(f"Please wait {remaining_time.seconds} seconds before using /everyone again.")

async def fetch_user_ids_command(update: Update, context):
    user_ids = get_user_ids()
    user_details_list = []
    for user_id in user_ids:
        first_name, last_name, username = get_user_details(user_id)
        user_details_list.append(f"{user_id} - {first_name} {last_name} (@{username})")
    user_details_str = "\n".join(user_details_list)
    await update.message.reply_text(f"Stored User Details:\n{user_details_str}")

@app.post("/webhook")
async def webhook(request: Request):
    webhook_data = await request.json()
    bot = Bot(token=myBotToken)
    update = Update.de_json(webhook_data, bot)
    dispatcher = Dispatcher(bot, None, workers=4)

    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram_reels))
    dispatcher.add_handler(CommandHandler("everyone", mention_all))
    dispatcher.add_handler(CommandHandler("fetch", fetch_user_ids_command))

    dispatcher.process_update(update)
    return {"message": "ok"}

@app.get("/")
def index():
    return {"message": "Hello World"}

if __name__ == "__main__":
    init_db()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    application = Application.builder().token(myBotToken).build()
    application.run_polling()
