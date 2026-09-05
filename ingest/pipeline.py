import os
import re
import json
import logging
import pandas as pd
from ingest import config
from ingest.connectors.app_store_connector import AppStoreConnector
from ingest.connectors.play_store_connector import PlayStoreConnector
from ingest.connectors.reddit_connector import RedditConnector
from ingest.connectors.youtube_connector import YouTubeConnector

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Main Orchestrator for Phase 1 Ingestion.
    Downloads, cleans, sanitizes, and saves raw reviews and comments.
    """
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or config.RAW_DATA_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_text(self, text):
        if not text:
            return ""
        # 1. Strip HTML tags
        text = re.sub(r'<[^>]*>', '', text)
        # 2. Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # 3. Simple PII masking (emails & phone numbers)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', text)
        text = re.sub(r'\b\d{10}\b|\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b', '[PHONE_REDACTED]', text)
        return text

    def sanitize_data(self, records):
        """
        Removes duplicates, drops empty records, and cleans texts.
        """
        if not records:
            return []

        df = pd.DataFrame(records)
        
        # Fill missing values
        df['text'] = df['text'].fillna('')
        
        # Clean text field
        df['text'] = df['text'].apply(self.clean_text)
        
        # Drop empty texts
        df = df[df['text'].str.strip() != '']
        
        # Remove duplicates based on the 'text' field
        df = df.drop_duplicates(subset=['text'])
        
        return df.to_dict(orient='records')

    def run(self, limit_per_source=100):
        all_data = []

        # 1. Fetch Apple App Store reviews
        app_store = AppStoreConnector()
        app_reviews = app_store.fetch_reviews(limit=limit_per_source)
        all_data.extend(app_reviews)

        # 2. Fetch Google Play Store reviews
        play_store = PlayStoreConnector()
        play_reviews = play_store.fetch_reviews(limit=limit_per_source)
        all_data.extend(play_reviews)

        # 3. Fetch Reddit posts/discussions
        reddit = RedditConnector()
        reddit_posts = reddit.fetch_discussions(limit=limit_per_source)
        all_data.extend(reddit_posts)

        # 4. Fetch YouTube comments
        youtube = YouTubeConnector()
        yt_comments = youtube.fetch_comments(limit=limit_per_source)
        all_data.extend(yt_comments)

        logger.info(f"Total raw items fetched: {len(all_data)}")

        # Clean and sanitize
        sanitized_data = self.sanitize_data(all_data)
        logger.info(f"Total sanitized items after de-duplication: {len(sanitized_data)}")

        # Save to output file
        output_filepath = os.path.join(self.output_dir, "raw_feedback.json")
        with open(output_filepath, "w", encoding="utf-8") as f:
            json.dump(sanitized_data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Successfully saved raw feedback dataset to: {output_filepath}")
        return output_filepath
