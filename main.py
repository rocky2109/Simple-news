import os
import random
import feedparser
import html
import re
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    JobQueue,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your bot token
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Your channel or user chat ID

# RSS Feeds for English, Hindi, Gujarati
RSS_FEEDS = {
    "English": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "Hindi": "https://www.bhaskar.com/rss-feed/2278/",
    "Gujarati": "https://www.divyabhaskar.co.in/rss-feed/74/"
}

# Cache to avoid repeat news
sent_links = set()

def extract_image(entry):
    match = re.search(r'<img[^>]+src="([^"]+)"', entry.get("summary", ""))
    return match.group(1) if match else None

def fetch_random_news():
    lang, feed_url = random.choice(list(RSS_FEEDS.items()))
    feed = feedparser.parse(feed_url)

    if not feed.entries:
        return None, None

    # Try up to 5 times to get a new article
    for _ in range(5):
        entry = random.choice(feed.entries)
        if entry.link not in sent_links:
            break
    else:
        return None, None  # All are repeated

    title = html.unescape(entry.title)
    summary = html.unescape(re.sub(r'<[^>]+>', '', entry.get("summary", "")))[:280].rstrip() + "..."
    link = entry.link
    image = extract_image(entry)

    sent_links.add(link)  # Mark this news as sent

    message = f"🗞️ *{lang} News*\n\n*{title}*\n\n{summary}\n\n🔗 [Read more]({link})"
    return message, image

async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, img = fetch_random_news()
    if not msg:
        await update.message.reply_text("⚠️ No fresh news found right now.")
        return

    if img:
        await update.message.reply_photo(photo=img, caption=msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def auto_post_news(context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg, img = fetch_random_news()

    if msg:
        if img:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=img, caption=msg, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
    else:
        await bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No fresh news found in RSS feeds.")

async def on_startup(app):
    # Immediate post on start
    context = ContextTypes.DEFAULT_TYPE()
    await auto_post_news(context)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", send_news))

    # Job queue for auto-posting every 2 minutes (testing)
    

    print("✅ News bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
