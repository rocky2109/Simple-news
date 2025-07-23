import os
import random
import re
import html
import feedparser
import logging
from typing import Optional, Tuple
from telegram import Bot, Update, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

class EduNewsBot:
    """Educational News Bot with enhanced features."""
    
    def __init__(self):
        self.RSS_FEEDS = {
            "Gujarati": "https://www.sandesh.com/rss/gujarat",
            "Hindi": "https://www.bhaskar.com/rss-feed/2278/",
            "English": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "Technology": "https://feeds.feedburner.com/ndtvnews-technology-news",
            "Science": "https://www.sciencedaily.com/rss/all.xml"
        }
        
        self.EDUCATION_KEYWORDS = {
            'education', 'school', 'college', 'university', 'student', 'teacher',
            'learning', 'exam', 'academic', 'study', 'research', 'curriculum',
            'scholarship', 'literacy', 'campus', 'tuition', 'degree', 'lecture',
            'training', 'pedagogy', 'syllabus', 'educational', 'institute'
        }
        
        self.MAX_SUMMARY_LENGTH = 300
        self.DEFAULT_ERROR_MSG = "⚠️ No educational news found at the moment. Try again later!"
        self.MAX_ATTEMPTS = 5

    def is_educational(self, content: str) -> bool:
        """Check if content contains education-related keywords with context awareness."""
        content = content.lower()
        # Exclude false positives
        if any(word in content for word in ['school of thought', 'school shooting']):
            return False
        return any(re.search(rf'\b{re.escape(keyword)}\b', content) 
               for keyword in self.EDUCATION_KEYWORDS)

    def extract_media(self, entry: dict) -> Tuple[Optional[str], Optional[str]]:
        """Extracts both image and video URLs from entry content."""
        summary = entry.get("summary", "") + entry.get("content", "")
        
        # Extract first image
        img_match = re.search(r'<img[^>]+src="([^"]+)"', summary)
        image = img_match.group(1) if img_match else None
        
        # Extract first video (YouTube/Vimeo)
        video_match = re.search(
            r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|vimeo\.com/)[\w-]+)',
            summary
        )
        video = video_match.group(1) if video_match else None
        
        return image, video

    def clean_content(self, text: str) -> str:
        """Enhanced HTML cleaning with special character handling."""
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
        return text

    def format_message(self, lang: str, title: str, summary: str, link: str) -> str:
        """Formats the news message with emoji and markdown."""
        return (
            f"📚 *{lang} Education News*\n\n"
            f"🔹 *{title}*\n\n"
            f"ℹ️ {summary}\n\n"
            f"🌐 [Read Full Article]({link})"
        )

    def fetch_educational_news(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Enhanced news fetcher with better error handling and filtering."""
        for _ in range(self.MAX_ATTEMPTS):
            try:
                lang, feed_url = random.choice(list(self.RSS_FEEDS.items()))
                feed = feedparser.parse(feed_url)
                
                if not feed.entries:
                    continue
                    
                # Filter and score entries
                scored_entries = []
                for entry in feed.entries:
                    content = entry.title + entry.get("summary", "")
                    if self.is_educational(content):
                        score = sum(
                            1 for keyword in self.EDUCATION_KEYWORDS 
                            if re.search(rf'\b{re.escape(keyword)}\b', content.lower())
                        )
                        scored_entries.append((score, entry))
                
                if not scored_entries:
                    continue
                    
                # Get entry with highest education keyword matches
                scored_entries.sort(reverse=True)
                entry = scored_entries[0][1]
                
                title = self.clean_content(entry.title)
                summary = self.clean_content(entry.get("summary", ""))[:self.MAX_SUMMARY_LENGTH]
                link = entry.link
                image, video = self.extract_media(entry)
                
                message = self.format_message(lang, title, summary, link)
                return message, image, video
                
            except Exception as e:
                logger.error(f"Error fetching news: {e}")
                continue
                
        return None, None, None

    async def send_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Enhanced news sender with media support."""
        msg, img, video = self.fetch_educational_news()
        
        if not msg:
            await update.message.reply_text(self.DEFAULT_ERROR_MSG)
            return
            
        try:
            if img:
                await update.message.reply_photo(
                    photo=img,
                    caption=msg,
                    parse_mode="MarkdownV2"
                )
            elif video:
                await update.message.reply_text(
                    f"{msg}\n\n🎥 [Watch Video]({video})",
                    parse_mode="MarkdownV2"
                )
            else:
                await update.message.reply_text(
                    msg,
                    parse_mode="MarkdownV2"
                )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await update.message.reply_text(
                "📰 " + msg.split("\n\n")[0] + "\n\n" + msg.split("\n\n")[-1],
                parse_mode="MarkdownV2"
            )

    async def on_startup(self, app) -> None:
        """Enhanced startup routine with channel posting."""
        bot = app.bot
        msg, img, video = self.fetch_educational_news()
        
        if not msg:
            logger.warning("No educational news found on startup")
            return
            
        try:
            if img:
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=img,
                    caption=msg,
                    parse_mode="MarkdownV2"
                )
            elif video:
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=f"{msg}\n\n🎥 [Watch Video]({video})",
                    parse_mode="MarkdownV2"
                )
            else:
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode="MarkdownV2"
                )
        except Exception as e:
            logger.error(f"Startup message failed: {e}")

    async def handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handles user feedback."""
        feedback = update.message.text
        logger.info(f"User feedback: {feedback}")
        await update.message.reply_text("📝 Thanks for your feedback!")

    def run(self):
        """Runs the bot with all handlers."""
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("edunews", self.send_news))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_feedback))
        
        # Startup routine
        app.post_init = self.on_startup
        
        # Error handler
        app.add_error_handler(self.error_handler)
        
        logger.info("Starting bot...")
        app.run_polling()

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Logs errors and sends user notifications."""
        logger.error(f"Update {update} caused error {context.error}")
        
        if isinstance(update, Update):
            await update.message.reply_text(
                "⚠️ An error occurred. Please try again later or use /edunews."
            )

if __name__ == "__main__":
    bot = EduNewsBot()
    bot.run()
