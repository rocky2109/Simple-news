import os
import random
import feedparser
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
import html
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Bot Token from environment
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Channel ID from environment

# 🌐 RSS Feeds categorized by language
RSS_FEEDS = {
    "English": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Hindi": "https://www.bhaskar.com/rss-feed/2278/",
    "Gujarati": "https://www.divyabhaskar.co.in/rss-feed/74/"
}

# 🖼️ Extract image URL from RSS entry
def extract_image(entry):
    match = re.search(r'<img[^>]+src="([^"]+)"', entry.get("summary", ""))
    return match.group(1) if match else None

# 📄 Fetch random news from all or specific feed
def fetch_news(lang_filter=None):
    feed_list = [(lang, url) for lang, url in RSS_FEEDS.items() if not lang_filter or lang == lang_filter]
    if not feed_list:
        return None, None

    lang, feed_url = random.choice(feed_list)
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

# 🎯 Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "👋 Welcome to the Multi-Language News Bot!\n\n"
        "You can use these commands:\n"
        "📰 /news - Random news from any language\n"
        "🇮🇳 /hindi - Get latest Hindi news\n"
        "🇬🇧 /english - Get latest English news\n"
        "🇬🇺 /gujarati - Get latest Gujarati news"
    )
    await update.message.reply_text(welcome)

async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, img = fetch_news()
    if not msg:
        await update.message.reply_text("⚠️ No news found.")
        return
    if img:
        await update.message.reply_photo(photo=img, caption=msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def send_lang_news(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    msg, img = fetch_news(lang)
    if not msg:
        await update.message.reply_text(f"⚠️ No {lang} news found.")
        return
    if img:
        await update.message.reply_photo(photo=img, caption=msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

# Aliased handlers for language-specific commands
async def hindi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_lang_news(update, context, "Hindi")

async def english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_lang_news(update, context, "English")

async def gujarati(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_lang_news(update, context, "Gujarati")

# 🚀 Start Bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", send_news))
    app.add_handler(CommandHandler("hindi", hindi))
    app.add_handler(CommandHandler("english", english))
    app.add_handler(CommandHandler("gujarati", gujarati))
    print("✅ Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
