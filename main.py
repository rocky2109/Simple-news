import os
import requests
from datetime import datetime, timedelta
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # From environment or Koyeb Secret
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Example: "@yourchannel"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Your NewsAPI Key

def fetch_weekly_news():
    try:
        today = datetime.now()
        from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = today.strftime("%Y-%m-%d")

        url = (
            f"https://newsapi.org/v2/top-headlines?"
            f"country=in&category=general&pageSize=5&"
            f"from={from_date}&to={to_date}&apiKey={NEWS_API_KEY}"
        )

        r = requests.get(url, timeout=10)
        data = r.json()

        if data.get("status") != "ok" or not data.get("articles"):
            print("⚠️ No weekly news:", data.get("message"))
            return None

        return [
            {
                "title": a["title"],
                "summary": a.get("description") or "",
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
        "This bot posts weekly top Indian news headlines here.\n"
        "Use /start to check if it’s active.\n\n"
        "📰 Powered by [NewsAPI](https://newsapi.org)",
        parse_mode="Markdown"
    )


async def on_startup(app):
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text="🚀 Bot started! Fetching this week's top headlines...")

    news_list = fetch_weekly_news()
    if not news_list:
        return  # Do nothing if no news

    for news in news_list:
        caption = f"📰 *{news['title']}*\n\n{news['summary']}\n🔗 [Read more]({news['url']})"
        try:
            if news["image"]:
                await bot.send_photo(chat_id=CHANNEL_ID, photo=news["image"], caption=caption, parse_mode="Markdown")
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending message: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    app.run_polling()


if __name__ == "__main__":
    main()
