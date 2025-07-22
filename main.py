import requests
from telegram import Bot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Example: @yourchannel
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

def send_to_telegram(news):
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

if __name__ == "__main__":
    news = fetch_news()
    if news:
        send_to_telegram(news)
