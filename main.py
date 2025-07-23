import os
import random
import feedparser
import html
import re
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set this in environment
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Set this in environment (channel or chat ID)

# 🎯 RSS Feeds
RSS_FEEDS = {
    "English": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Hindi": "https://www.bhaskar.com/rss-feed/2278/",
    "Gujarati": "https://www.divyabhaskar.co.in/rss-feed/74/"
}

# 🔍 Extract image if available
def extract_image(entry):
    match = re.search(r'<img[^>]+src="([^"]+)"', entry.get("summary", ""))
    return match.group(1) if match else None

# 📦 Fetch random news from any RSS
def fetch_random_news():
    lang, feed_url = random.choice(list(RSS_FEEDS.items()))
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        return None, None

    entry = random.choice(feed.entries)
    title = html.unescape(entry.title)
    summary = html.unescape(re.sub(r'<[^>]+>', '', entry.get("summary", "")))[:300]
    link = entry.link
    image = extract_image(entry)

    message = f"🗞️ *{lang} News*\n\n*{title}*\n\n{summary}\n\n🔗 [Read more]({link})"
    return message, image

# ⚡ /start and /news commands
async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, img = fetch_random_news()
    if not msg:
        await update.message.reply_text("⚠️ No news found at the moment.")
        return

    if img:
        await update.message.reply_photo(photo=img, caption=msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

# 🚀 Run once at startup
async def on_startup(app):
    bot = Bot(BOT_TOKEN)

    # ✅ Send startup message
    await bot.send_message(chat_id=CHANNEL_ID, text="✅ Bot started.")

    # 📰 Send one news item on startup
    msg, img = fetch_random_news()
    if msg:
        if img:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=img, caption=msg, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")

# 🚦 Main entry
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", send_news))
    app.post_init = on_startup
    app.run_polling()

if name == "main":
    main()
