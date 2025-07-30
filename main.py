import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

openai.api_key = os.getenv("OPENAI_API_KEY")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

client = openai.OpenAI(api_key=openai.api_key)
chat_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that receives raw trade alerts and reformats them into a clean, human-readable summary. Only extract relevant trading information like ticker, option strike/expiry, entry, stop loss, and profit targets. Format in bullet points and use emoji headers like 📊 or 🔔."
        },
        {"role": "user", "content": user_message}
    ]
)

    gpt_reply = chat_response.choices[0].message.content
    await update.message.reply_text(f"📩 GPT-4o Reply:\n{gpt_reply}")

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()

