import os
import base64
import asyncio
from telethon import TelegramClient, events
from openai import OpenAI
from telegram import Bot

print("🔥 main.py loaded")

# 🔄 Decode and save session file
part1 = os.getenv("SESSION_B64_P1", "")
part2 = os.getenv("SESSION_B64_P2", "")
session_b64 = part1 + part2
with open("telethon.session", "wb") as f:
    f.write(base64.b64decode(session_b64))
print("✅ Session file decoded and saved.")

# 🔐 Load environment variables
api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
channel_id = int(os.getenv("CHANNEL_ID"))  # Use numeric ID for private channel
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = int(os.getenv("CHAT_ID"))

# 🚀 Setup OpenAI and Telegram bot
openai_client = OpenAI(api_key=openai_api_key)
bot = Bot(token=telegram_bot_token)

# 📡 Initialize Telegram client
client = TelegramClient("telethon.session", api_id, api_hash)

async def main():
    print("🚀 Starting Telethon client...")
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Session unauthorized. Re-upload session.")
        return

    try:
        # Cache entity for private channel
        entity = await client.get_entity(channel_id)
        print("📌 Channel entity cached.")

        @client.on(events.NewMessage(chats=entity))
        async def handler(event):
            try:
                msg = event.message.message
                print(f"📩 New message: {msg[:60]}...")

                # Summarize with GPT
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Summarize and explain this trading alert in simple English."},
                        {"role": "user", "content": msg}
                    ]
                )
                gpt_reply = response.choices[0].message.content

                await bot.send_message(chat_id=chat_id, text=gpt_reply)
                print("✅ Sent GPT response to Telegram.")

            except Exception as e:
                print(f"⚠️ Error handling message: {e}")

        print("🛰️ Listening for messages...")
        await client.run_until_disconnected()

    except Exception as e:
        print(f"❌ Startup Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())