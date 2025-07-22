import requests
import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # For auto news post
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

def send_news_to_channel():
    news = fetch_news()
    if not news:
        return
    bot = Bot(token=BOT_TOKEN)
    caption = f"""📰 *{news['title']}*

{news['summary']}

🔗 [Read more]({news['url']})
"""
    bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=news['image'] if news['image'] else "https://via.placeholder.com/512",
        caption=caption,
        parse_mode="Markdown"
    )

def send_startup_message():
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(
        chat_id=CHANNEL_ID,
        text="🚀 *News Bot has started successfully!*",
        parse_mode="Markdown"
    )

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Hello! I'm your Indian News Bot.\n\nI'll keep your channel updated with the latest Indian news headlines hourly.\n\n✅ Deployed & ready!"
    )

def main():
    send_startup_message()
    send_news_to_channel()  # Optional: auto-send news on startup

    # Set up command listener
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
