import os
import requests
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # e.g. "@yourchannel" or -1001234567890
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_news():
    url = f"https://api.worldnewsapi.com/search-news?text=India&language=en&number=1&api-key={NEWS_API_KEY}"
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 I'm your Indian News Bot! I'll post the latest news to your channel automatically.")


async def on_startup(app):
    # Send bot started message to channel
    bot = Bot(BOT_TOKEN)
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 News Bot has started successfully!"
    )

    # Optional: send one news article on startup
    news = fetch_news()
    if news:
        caption = f"📰 *{news['title']}*\n\n{news['summary']}\n\n🔗 [Read more]({news['url']})"
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=news['image'] if news['image'] else "https://via.placeholder.com/512",
            caption=caption,
            parse_mode="Markdown"
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.post_init = on_startup
    app.run_polling()


if __name__ == "__main__":
    main()
