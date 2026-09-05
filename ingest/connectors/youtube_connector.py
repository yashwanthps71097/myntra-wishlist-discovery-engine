import logging
import datetime
import random
from ingest import config

logger = logging.getLogger(__name__)

MOCK_YOUTUBE_COMMENTS = [
    "I wishlisted this dress from the haul video but I'm so scared the fabric will feel cheap in person. Anyone bought it?",
    "Every time Myntra says 'EORS is live', the prices of the wishlisted items actually increase! Such a scam, not buying now.",
    "Wishlisted this jacket. It's beautiful but 4999 INR is just too expensive for Roadster quality. Waiting for a 60% off coupon.",
    "Myntra sizing is so weird. I'm usually an M but the size chart for this brand says L. Leaving it in my wishlist until I can check store sizes.",
    "I had these boots wishlisted for a month. Today they went on sale, but my size (UK 8) sold out in literally 5 minutes! Heartbroken.",
    "Is it just me or does the wishlist not notify you at all when prices drop? I only checked today by chance and saw it was 30% off."
]

class YouTubeConnector:
    """
    Connects to YouTube Data API to fetch comments on Myntra fashion hauls and review videos.
    Falls back to mock data if API key is not configured.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or config.YOUTUBE_API_KEY
        self.use_real_api = config.has_youtube_creds()
        
        if self.use_real_api:
            try:
                from googleapiclient.discovery import build
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize YouTube API client: {e}. Falling back to mock mode.")
                self.use_real_api = False
        else:
            logger.info("No YouTube API credentials found. Using fallback mock mode.")

    def fetch_comments(self, video_ids=["dQw4w9WgXcQ"], query="Myntra wishlist", limit=50):
        if not self.use_real_api:
            logger.info(f"Generating mock YouTube comments for query: '{query}'...")
            return self._generate_mock_comments(limit)

        logger.info(f"Fetching comments from YouTube for videos: {video_ids}...")
        comments = []
        try:
            for video_id in video_ids:
                request = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(limit, 100),
                    textFormat="plainText"
                )
                response = request.execute()
                
                for item in response.get("items", []):
                    snippet = item["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "id": f"yt_{item['id']}",
                        "author": snippet.get("authorDisplayName", "Anonymous"),
                        "title": "",
                        "text": snippet.get("textDisplay", ""),
                        "rating": snippet.get("likeCount", 0),
                        "timestamp": snippet.get("publishedAt"),
                        "platform": "YouTube"
                    })
            logger.info(f"Successfully fetched {len(comments)} comments from YouTube.")
            return comments
        except Exception as e:
            logger.error(f"Error fetching YouTube comments: {e}. Falling back to mock data.")
            return self._generate_mock_comments(limit)

    def _generate_mock_comments(self, limit):
        results = []
        for i in range(limit):
            comment_text = random.choice(MOCK_YOUTUBE_COMMENTS)
            hours_ago = random.randint(1, 1000)
            ts = datetime.datetime.now() - datetime.timedelta(hours=hours_ago)
            results.append({
                "id": f"mock_yt_{i}_{random.randint(1000, 9999)}",
                "author": f"user_{random.randint(100, 999)}",
                "title": "",
                "text": comment_text,
                "rating": random.randint(0, 15),
                "timestamp": ts.isoformat(),
                "platform": "YouTube"
            })
        return results
