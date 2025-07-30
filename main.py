import os
import asyncio
from telethon import TelegramClient, events
from openai import OpenAI
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

# --- Telegram API credentials (user account) ---
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel_username = os.getenv("CHANNEL_USERNAME")  # e.g., -100xxxxxxxxxx

# --- OpenAI setup ---
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Telegram bot credentials (to send GPT summary back to you) ---
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")  # Your personal Telegram user ID
bot = Bot(token=telegram_bot_token)

# --- Telethon client (logs in as your real user) ---
client = TelegramClient("session", api_id, api_hash)

@client.on(events.NewMessage(chats=channel_username))
async def handle_message(event):
    text = event.raw_text
    print(f"\n📩 New message:\n{text}")

    try:
        # Send to GPT-4o
        chat_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're a trade alert assistant. Summarize clearly and concisely. Add emojis and structure if helpful."},
                {"role": "user", "content": text}
            ]
        )
        gpt_reply = chat_response.choices[0].message.content
        print(f"\n🤖 GPT Summary:\n{gpt_reply}")

        # Optional: Send back to your Telegram via bot
        bot.send_message(chat_id=telegram_chat_id, text=gpt_reply)

    except Exception as e:
        print(f"⚠️ Error: {e}")

async def main():
    await client.start()
    print("✅ Bot is running... Listening for new messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
