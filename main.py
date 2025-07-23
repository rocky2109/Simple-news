import os
import random
import feedparser
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import html
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Add your bot token here
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Or use chat_id for testing

# 🎯 List of RSS feeds
RSS_FEEDS = {
    "English": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Hindi": "https://www.bhaskar.com/rss-feed/2278/",
    "Gujarati": "https://www.divyabhaskar.co.in/rss-feed/74/"
}

def extract_image(entry):
    # Some RSS feeds include image inside summary as <img>
    match = re.search(r'<img[^>]+src="([^"]+)"', entry.get("summary", ""))
    return match.group(1) if match else None

def fetch_random_news():
    lang, feed_url = random.choice(list(RSS_FEEDS.items()))
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        return None, None

    entry = random.choice(feed.entries)
    title = html.unescape(entry.title)
    summary = html.unescape(re.sub(r'<[^>]+>', '', entry.get("summary", "")))[:300]  # Clean HTML
    link = entry.link
    image = extract_image(entry)

    message = f"🗞️ *{lang} News*\n\n*{title}*\n\n{summary}\n\n🔗 [Read more]({link})"
    return message, image

async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, img = fetch_random_news()
    if not msg:
        await update.message.reply_text("⚠️ No news found at the moment.")
        return

    if img:
        await update.message.reply_photo(photo=img, caption=msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def on_startup(app):
    bot = Bot(BOT_TOKEN)
    msg, img = fetch_random_news()

    if msg:
        if img:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=img, caption=msg, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
    else:
        await bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No fresh RSS news found.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", send_news))
    app.post_init = on_startup
    app.run_polling()

Bot().run()
