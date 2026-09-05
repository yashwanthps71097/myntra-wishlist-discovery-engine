import logging
import requests
import datetime

logger = logging.getLogger(__name__)

class AppStoreConnector:
    """
    Fetches reviews for the Myntra app from the Apple App Store RSS Feed.
    App ID for Myntra: 907394059 (Myntra - Fashion Shopping App)
    """
    def __init__(self, app_id=907394059, country="in"):
        self.app_id = app_id
        self.country = country

    def fetch_reviews(self, limit=100):
        try:
            logger.info(f"Fetching reviews from Apple App Store RSS feed for App ID: {self.app_id}...")
            # Fetch the JSON feed (max limit on RSS is 50 per page usually, we can fetch page 1)
            url = f"https://itunes.apple.com/{self.country}/rss/customerreviews/id={self.app_id}/sortBy=mostRecent/json"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            feed = data.get("feed", {})
            entries = feed.get("entry", [])
            
            # If only one review exists, entry might be a dict instead of a list
            if isinstance(entries, dict):
                entries = [entries]
                
            reviews = []
            for entry in entries:
                # The first entry in the RSS JSON can sometimes be the app metadata itself, skip if it doesn't have an author
                if "author" not in entry:
                    continue
                    
                author = entry.get("author", {}).get("name", {}).get("label", "Anonymous")
                title = entry.get("title", {}).get("label", "")
                text = entry.get("content", {}).get("label", "")
                rating = int(entry.get("im:rating", {}).get("label", 0))
                id_val = entry.get("id", {}).get("label", "")
                
                # Parse timestamp if available
                timestamp = None
                # iTunes RSS feeds usually don't have a structured date field per entry in JSON format,
                # but we can default to the current time or parse it if present.
                
                reviews.append({
                    "id": str(id_val),
                    "author": author,
                    "title": title,
                    "text": text,
                    "rating": rating,
                    "timestamp": datetime.datetime.now().isoformat(), # Fallback timestamp
                    "platform": "App Store"
                })
                
                if len(reviews) >= limit:
                    break
                    
            logger.info(f"Successfully fetched {len(reviews)} reviews from App Store RSS.")
            return reviews
        except Exception as e:
            logger.error(f"Error fetching App Store reviews: {e}")
            return []
