import os
import random
import re
import html
import feedparser
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Original RSS feeds (same as before)
RSS_FEEDS = {
    "Gujarati": "https://www.sandesh.com/rss/gujarat",
    "Hindi": "https://www.bhaskar.com/rss-feed/2278/",
    "English": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
}

# Keywords to identify educational content
EDUCATION_KEYWORDS = {
    'education', 'school', 'college', 'university', 'student', 'teacher',
    'learning', 'exam', 'academic', 'study', 'research', 'curriculum',
    'scholarship', 'literacy', 'campus', 'tuition', 'degree', 'lecture',
    'training', 'pedagogy', 'syllabus', 'educational', 'institute'
}

MAX_SUMMARY_LENGTH = 300
DEFAULT_ERROR_MSG = "⚠️ No educational news found at the moment."

def is_educational(content: str) -> bool:
    """Check if content contains education-related keywords."""
    content = content.lower()
    return any(keyword in content for keyword in EDUCATION_KEYWORDS)

def extract_image(entry: dict) -> str | None:
    """Extracts first image URL from entry content."""
    match = re.search(r'<img[^>]+src="([^"]+)"', entry.get("summary", ""))
    return match.group(1) if match else None

def clean_html(text: str) -> str:
    """Removes HTML tags and unescapes HTML entities."""
    return html.unescape(re.sub(r'<[^>]+>', '', text))

def fetch_educational_news(max_attempts: int = 3) -> tuple[str | None, str | None]:
    """Fetches random educational news with category filtering."""
    attempts = 0
    while attempts < max_attempts:
        try:
            lang, feed_url = random.choice(list(RSS_FEEDS.items()))
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                continue

            # Filter for educational content
            educational_entries = [
                entry for entry in feed.entries
                if is_educational(entry.title + entry.get("summary", ""))
            ]

            if not educational_entries:
                attempts += 1
                continue

            entry = random.choice(educational_entries)
            title = clean_html(entry.title)
            summary = clean_html(entry.get("summary", ""))[:MAX_SUMMARY_LENGTH]
            link = entry.link
            image = extract_image(entry)

            message = (
                f"📚 *Latest News ({lang})*\n\n"
                f"*{title}*\n\n"
                f"{summary}\n\n"
                f"🔗 [Read more]({link})"
            )
            return message, image

        except Exception as e:
            print(f"Attempt {attempts + 1} failed: {e}")
            attempts += 1

    return None, None

async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /edunews command."""
    msg, img = fetch_educational_news()
    
    if not msg:
        await update.message.reply_text(DEFAULT_ERROR_MSG)
        return

    if img:
        await update.message.reply_photo(
            photo=img, 
            caption=msg, 
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            msg, 
            parse_mode="Markdown",
            
        )

async def on_startup(app) -> None:
    """Sends initial educational news when bot starts."""
    bot = Bot(BOT_TOKEN)
    msg, img = fetch_educational_news()

    if msg:
        if img:
            await bot.send_photo(
                chat_id=CHANNEL_ID, 
                photo=img, 
                caption=msg, 
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID, 
                text=msg, 
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

def main() -> None:
    """Main application entry point."""
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("edunews", send_news))  # Changed to education-specific command
    app.post_init = on_startup
    app.run_polling()

if __name__ == "__main__":
    main()
