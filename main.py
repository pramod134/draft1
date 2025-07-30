import os
import base64
import asyncio
from telethon import TelegramClient, events
import openai
import telegram

# === Load environment variables ===
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel_username = os.getenv("CHANNEL_USERNAME")
session_b64 = os.getenv("SESSION_B64")
openai.api_key = os.getenv("OPENAI_API_KEY")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = int(os.getenv("CHAT_ID"))  # ✅ Final destination for the GPT response

# === Decode and save Telethon session ===
with open("session.session", "wb") as f:
    f.write(base64.b64decode(session_b64))

# === Telegram Clients ===
client = TelegramClient("session.session", api_id, api_hash)
bot = telegram.Bot(token=bot_token)

# === GPT Function ===
async def ask_gpt(message):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant summarizing financial trade alerts."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

# === Message Handler ===
@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    text = event.message.message
    print(f"📩 Incoming message:\n{text}")

    try:
        reply = await ask_gpt(text)
        print(f"🤖 GPT reply:\n{reply}")

        await bot.send_message(chat_id=chat_id, text=reply)

    except Exception as e:
        print(f"❌ Error processing message: {e}")

# === Main Runner ===
async def main():
    await client.start()
    print("🚀 Telethon client started and listening for messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
