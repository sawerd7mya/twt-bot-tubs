import tweepy
import telegram
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TWITTER_USERS = os.getenv("TWITTER_USERS").split(",")

bot = telegram.Bot(token=BOT_TOKEN)
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN, wait_on_rate_limit=True)

last_tweet_ids = {}  # user_id -> last tweet id

async def check_tweets_for_user(username):
    global last_tweet_ids
    try:
        user = client.get_user(username=username.strip())
        user_id = user.data.id

        tweets = client.get_users_tweets(id=user_id, max_results=2)
        if tweets.data:
            latest_tweet = tweets.data[0]
            last_seen_id = last_tweet_ids.get(user_id)

            if not last_seen_id or latest_tweet.id != last_seen_id:
                tweet_url = f"https://twitter.com/{username}/status/{latest_tweet.id}"
                await bot.send_message(chat_id=CHAT_ID, text=f"📝 Новый твит от {username}:{tweet_url}")
                last_tweet_ids[user_id] = latest_tweet.id
            else:
                print(f"Нет новых твитов у @{username}.")
        else:
            print(f"У @{username} нет твитов.")
    except Exception as e:
        print(f"Ошибка при проверке @{username}: {e}")

async def main_loop():
    while True:
        await check_tweets_for_user(TWITTER_USERS[0])
        await asyncio.sleep(300)  # проверять каждые 5 минут

if __name__ == "__main__":
    asyncio.run(main_loop())
