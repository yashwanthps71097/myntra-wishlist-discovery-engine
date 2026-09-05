import logging
import datetime
import random
from ingest import config

logger = logging.getLogger(__name__)

# Sample Mock comments reflecting the actual domain problem: Myntra wishlist conversions
MOCK_REDDIT_POSTS = [
    {
        "id": "mock_r1",
        "author": "fashion_lover99",
        "title": "Why do we keep items in wishlist forever?",
        "text": "Honestly, I have like 50 items in my Myntra wishlist right now. Most of them have been there for over 2 months. I think I'm just waiting for a massive discount or EORS sale, but by the time the sale comes, my size is always out of stock! It's so frustrating.",
        "rating": 15,
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": "Reddit"
    },
    {
        "id": "mock_r2",
        "author": "kartik_sharma",
        "title": "Fit issues on Myntra Roadster shirts?",
        "text": "I really want to buy the Roadster casual denim shirt in my wishlist, but the sizing reviews are so mixed. Some say buy one size larger, others say it fits true to size. I don't want to buy and then go through the hassle of return and exchange.",
        "rating": 8,
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": "Reddit"
    },
    {
        "id": "mock_r3",
        "author": "ria_v",
        "title": "Myntra wishlist vs buying immediately",
        "text": "I wishlisted a gorgeous Anouk Kurta set. I waited 3 weeks to see if the price drops. It didn't drop, and now it's out of stock. Wish Myntra notified me when it was down to last 2 items, I would have bought it.",
        "rating": 23,
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": "Reddit"
    },
    {
        "id": "mock_r4",
        "author": "shoe_head",
        "title": "Nike Air Max price drops on Myntra?",
        "text": "Is it just me or do Nike shoes on Myntra fluctuate in price daily? I've kept 3 shoes wishlisted and the prices go up and down by 500 rupees every day. It's impossible to know when to click buy.",
        "rating": 4,
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": "Reddit"
    },
    {
        "id": "mock_r5",
        "author": "priya_gupta",
        "title": "Delivery charges Myntra",
        "text": "I had a top in my wishlist for weeks. Finally decided to buy it since it was on sale for 299, but Myntra added 99 rupees delivery charge at checkout because order value was under 799. I just ended up leaving it in the cart and not buying.",
        "rating": 12,
        "timestamp": datetime.datetime.now().isoformat(),
        "platform": "Reddit"
    }
]

class RedditConnector:
    """
    Connects to Reddit API to fetch discussions from subreddits like r/IndiaFashionStore or r/Myntra.
    Falls back to mock data if credentials are not configured.
    """
    def __init__(self, client_id=None, client_secret=None, user_agent=None):
        self.client_id = client_id or config.REDDIT_CLIENT_ID
        self.client_secret = client_secret or config.REDDIT_CLIENT_SECRET
        self.user_agent = user_agent or config.REDDIT_USER_AGENT
        
        self.use_real_api = config.has_reddit_creds()
        if self.use_real_api:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    user_agent=self.user_agent
                )
            except Exception as e:
                logger.error(f"Failed to initialize PRAW: {e}. Falling back to mock mode.")
                self.use_real_api = False
        else:
            logger.info("No Reddit API credentials found. Using fallback mock mode.")

    def fetch_discussions(self, subreddits=["IndiaFashionStore", "Myntra"], query="wishlist OR buying", limit=50):
        if not self.use_real_api:
            logger.info(f"Generating mock Reddit discussions for search: '{query}'...")
            return self._generate_mock_posts(limit)

        logger.info(f"Searching Reddit for '{query}' in subreddits {subreddits}...")
        posts = []
        try:
            for sub_name in subreddits:
                subreddit = self.reddit.subreddit(sub_name)
                # Search within subreddit
                for submission in subreddit.search(query, limit=limit):
                    posts.append({
                        "id": f"reddit_{submission.id}",
                        "author": str(submission.author),
                        "title": submission.title,
                        "text": submission.selftext if submission.selftext else submission.title,
                        "rating": submission.score,
                        "timestamp": datetime.datetime.fromtimestamp(submission.created_utc).isoformat(),
                        "platform": "Reddit"
                    })
            logger.info(f"Successfully fetched {len(posts)} posts from Reddit.")
            return posts
        except Exception as e:
            logger.error(f"Error fetching Reddit discussions: {e}. Falling back to mock data.")
            return self._generate_mock_posts(limit)

    def _generate_mock_posts(self, limit):
        results = []
        for i in range(limit):
            base_post = random.choice(MOCK_REDDIT_POSTS)
            post_copy = base_post.copy()
            post_copy["id"] = f"mock_reddit_{i}_{random.randint(1000, 9999)}"
            # Jitter timestamp slightly
            hours_ago = random.randint(1, 720)
            ts = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
            post_copy["timestamp"] = ts.isoformat()
            results.append(post_copy)
        return results
