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
            f"country=in&"
            f"category=general&"
            f"from={get_today()}&"
            f"apiKey={NEWS_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        if data.get("status") != "ok" or not data.get("articles"):
            return None

        # Return the first news article
        article = data["articles"][0]
        return {
            "title": article["title"],
            "summary": article["description"] or "",
            "url": article["url"],
            "image": article["urlToImage"] or None,
        }

    except Exception as e:
        print(f"[❌] Error fetching news: {e}")
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
