import logging
from google_play_scraper import Sort, reviews

logger = logging.getLogger(__name__)

class PlayStoreConnector:
    """
    Fetches reviews for the Myntra app from the Google Play Store.
    App ID for Myntra: com.myntra.android
    """
    def __init__(self, app_id="com.myntra.android", country="in", lang="en"):
        self.app_id = app_id
        self.country = country
        self.lang = lang

    def fetch_reviews(self, limit=100):
        try:
            logger.info(f"Fetching reviews from Play Store for '{self.app_id}'...")
            result, _ = reviews(
                self.app_id,
                lang=self.lang,
                country=self.country,
                sort=Sort.NEWEST,
                count=limit
            )
            
            formatted_reviews = []
            for rev in result:
                formatted_reviews.append({
                    "id": rev.get("reviewId", ""),
                    "author": rev.get("userName", "Anonymous"),
                    "title": "", # Play Store reviews don't have separate titles
                    "text": rev.get("content", ""),
                    "rating": rev.get("score", 0),
                    "timestamp": rev.get("at").isoformat() if rev.get("at") else None,
                    "platform": "Play Store"
                })
            logger.info(f"Successfully fetched {len(formatted_reviews)} reviews from Play Store.")
            return formatted_reviews
        except Exception as e:
            logger.error(f"Error fetching Play Store reviews: {e}")
            return []
