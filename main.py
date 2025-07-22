import os
import requests
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Environment variables (set on Koyeb)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g., "@yourchannel" or "-1001234567890"
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_news():
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        url = (
            f"https://api.worldnewsapi.com/search-news?"
            f"text=India&language=en&number=1&"
            f"min-publish-date={today}T00:00:00Z&"
            f"max-publish-date={today}T23:59:59Z&"
            f"api-key={NEWS_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()

        if "news" not in data or not data["news"]:
            return None

        news = data["news"][0]
        return {
            "title": news["title"],
            "summary": news["text"][:500] + "...",
            "url": news["url"],
            "image": news.get("image", None)
        }

    except Exception as e:
        print(f"Error fetching news: {e}")
        return None


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Indian News Bot!\n\n"
        "I’ll post the latest Indian news in your channel automatically. Stay tuned! 🇮🇳"
    )


# On startup (auto send news + startup ping)
async def on_startup(app):
    bot = Bot(BOT_TOKEN)

    # Bot startup message
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 News Bot has started successfully!"
    )

    # Fetch and send today's news
    news = fetch_news()
    if news:
        caption = f"📰 *{news['title']}*\n\n{news['summary']}\n\n🔗 [Read more]({news['url']})"

        try:
            if news['image']:
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
        except Exception as e:
            print(f"Error sending news: {e}")


# Main function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    app.run_polling()


if __name__ == "__main__":
    main()
