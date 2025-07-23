import os
import requests
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set in Koyeb Secret
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Telegram Channel ID like "@yourchannel"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Your NewsAPI key

from datetime import datetime, timedelta

def fetch_news():
    try:
        # Get date 7 days ago
        today = datetime.now()
        from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        url = (
            f"https://newsapi.org/v2/top-headlines?"
            f"country=in&category=general&from={from_date}&to={to_date}&"
            f"pageSize=3&apiKey={NEWS_API_KEY}"
        )

        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("status") != "ok" or not data.get("articles"):
            print("⚠️ No weekly news:", data.get("message"))
            return None

        return [
            {
                "title": a["title"],
                "summary": a.get("description") or a.get("content", ""),
                "url": a["url"],
                "image": a.get("urlToImage")
            }
            for a in data["articles"][:3]
        ]

    except Exception as e:
        print(f"[Error] fetch_news: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *Daily India News Bot* 🇮🇳\n\n"
        "This bot will post daily top Indian news headlines here.\n"
        "Use /start anytime to check it's working!",
        parse_mode="Markdown"
    )

async def on_startup(app):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text="🚀 Bot started. Fetching today's top headlines...")

    news_list = fetch_news()
    if not news_list:
        await bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No fresh news found today.")
        return

    for news in news_list:
        caption = f"📰 *{news['title']}*\n\n{news['summary']}\n🔗 [Read more]({news['url']})"
        if news["image"]:
            try:
                await bot.send_photo(chat_id=CHANNEL_ID, photo=news["image"],
                                     caption=caption, parse_mode="Markdown")
            except Exception:
                await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    app.run_polling()

if __name__ == "__main__":
    main()
