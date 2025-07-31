import os
import base64
import asyncio
from telethon import TelegramClient, events
import openai
import telegram

print("🔥 main.py loaded")  # Confirms the file started running

# === Load environment variables ===
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel_username = os.getenv("CHANNEL_USERNAME")
session_b64 = os.getenv("SESSION_B64")
openai.api_key = os.getenv("OPENAI_API_KEY")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = int(os.getenv("CHAT_ID"))

print("🔍 Checking environment variables:")
print(f"api_id: {api_id}")
print(f"api_hash: {api_hash[:4]}... (truncated)")
print(f"channel_username: {channel_username}")
print(f"bot_token: {bot_token[:4]}... (truncated)")
print(f"chat_id: {chat_id}")

# === Decode and save session file ===
try:
    with open("session.session", "wb") as f:
        f.write(base64.b64decode(session_b64))
    print("✅ Session file decoded and saved.")
except Exception as e:
    print(f"❌ Failed to decode session: {e}")

# === Telegram clients ===
client = TelegramClient("session.session", api_id, api_hash)
bot = telegram.Bot(token=bot_token)

# === GPT request function ===
async def ask_gpt(message):
    print("🤖 Sending message to GPT...")
    response = await openai.ChatCompletion.acreate(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant summarizing financial trade alerts."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

# === Message handler ===
@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    text = event.message.message
    print(f"📩 Incoming message:\n{text}")

    try:
        reply = await ask_gpt(text)
        print(f"🧠 GPT reply:\n{reply}")
        await bot.send_message(chat_id=chat_id, text=reply)
    except Exception as e:
        print(f"❌ Error processing message: {e}")

# === Main runner ===
async def main():
    print("🚀 Starting Telethon client...")
    await client.start()
    print("🛰️ Listening for messages...")
    await client.run_until_disconnected()

# === Run ===
if __name__ == "__main__":
    print("🧠 Starting asyncio main loop...")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Exception in main(): {e}")