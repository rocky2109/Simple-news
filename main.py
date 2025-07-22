import os
import requests
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g., "@mychannel" or "-1001234567890"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Get today's date
def get_today():
    return datetime.utcnow().strftime("%Y-%m-%d")

# Fetch current affairs/news from India
def fetch_news():
    try:
        url = (
            f"https://newsapi.org/v2/top-headlines?"
            f"country=in&category=general&"
            f"pageSize=1&"
            f"apiKey={NEWS_API_KEY}"
        )
        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("status") != "ok" or not data.get("articles"):
            print(f"No fresh news: {data.get('message')}")
            return None

        a = data["articles"][0]
        return {
            "title": a["title"],
            "summary": a.get("description") or a.get("content", ""),
            "url": a["url"],
            "image": a.get("urlToImage")
        }

    except Exception as e:
        print(f"[Error] fetch_news: {e}")
        return None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Indian News Bot!\n\n"
        "I’ll post the latest Indian current affairs in your channel automatically. 🇮🇳"
    )

# On bot startup
async def on_startup(app):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text="🚀 News Bot has started!")

    news = fetch_news()
    if news:
        caption = f"📰 *{news['title']}*\n\n{news['summary']}\n\n🔗 [Read More]({news['url']})"
        if news["image"]:
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=news["image"],
                caption=caption,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption,
                parse_mode="Markdown"
            )
    else:
        await bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No fresh news found today.")

# Main runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    app.run_polling()

if __name__ == "__main__":
    main()
