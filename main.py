import os
import asyncio
import random
import feedparser
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # like '@your_channel_username'

# RSS Feeds (Gujarati, Hindi, English)
RSS_FEEDS = [
    "https://gujaratsamachar.com/rss/gujarat",            # Gujarati
    "https://www.bhaskar.com/rss-national/",              # Hindi
    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",  # English
    "https://www.thehindu.com/news/national/feeder/default.rss",     # English
]

def fetch_random_rss_article():
    all_articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                all_articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:500],
                    "link": entry.get("link", ""),
                    "image": extract_image(entry)
                })
        except Exception as e:
            print(f"Error parsing feed {url}: {e}")

    if not all_articles:
        return None

    return random.choice(all_articles)

def extract_image(entry):
    # Common RSS image fields
    media_content = entry.get("media_content", [])
    if media_content:
        return media_content[0].get("url")
    # Some RSS feed may embed image in summary
    if "img" in entry.get("summary", ""):
        import re
        match = re.search(r'<img[^>]+src="([^">]+)"', entry["summary"])
        if match:
            return match.group(1)
    return None

async def post_news(bot: Bot):
    article = fetch_random_rss_article()
    if not article:
        await bot.send_message(chat_id=CHANNEL_ID, text="⚠️ No news found.")
        return

    caption = f"🗞 *{article['title']}*\n\n{article['summary']}\n\n🔗 [Read more]({article['link']})"

    try:
        if article["image"]:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=article["image"], caption=caption, parse_mode=ParseMode.MARKDOWN)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        print(f"Error sending message: {e}")

async def periodic_news(context: ContextTypes.DEFAULT_TYPE):
    await post_news(context.bot)

async def start(update, context):
    await update.message.reply_text("👋 Welcome! You’ll get auto-updated multilingual news every 2 minutes for testing.")

from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from telegram.ext import ApplicationBuilder, CommandHandler, JobQueue

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Bot started...")
    app.run_polling()

async def post_init(app):
    app.job_queue.run_repeating(periodic_news, interval=120, first=5)


if __name__ == "__main__":
    main()
