import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages local SQLite database schema creation and record insertions
    to support structured relational analytical queries.
    """
    def __init__(self, db_path="discovery.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """
        Creates SQLite tables if they do not exist.
        """
        logger.info(f"Initializing SQLite database at: {self.db_path}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Comments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    cluster_id INTEGER,
                    cluster_keywords TEXT,
                    platform TEXT,
                    rating INTEGER,
                    timestamp TEXT
                )
            """)
            
            # 2. Extractions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    comment_id TEXT PRIMARY KEY,
                    motivation TEXT,
                    primary_barrier TEXT,
                    intensity INTEGER,
                    user_segment TEXT,
                    FOREIGN KEY (comment_id) REFERENCES comments (id)
                )
            """)
            conn.commit()
        logger.info("Database schema initialized successfully.")

    def save_comment(self, record):
        """
        Inserts or replaces comment records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO comments (
                    id, text, cluster_id, cluster_keywords, platform, rating, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get("id"),
                record.get("text"),
                record.get("cluster_id"),
                ", ".join(record.get("cluster_keywords", [])),
                record.get("platform"),
                record.get("rating"),
                record.get("timestamp")
            ))
            conn.commit()

    def save_extraction(self, comment_id, ext):
        """
        Inserts or replaces extracted LLM structures.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO extractions (
                    comment_id, motivation, primary_barrier, intensity, user_segment
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                comment_id,
                ext.get("motivation", "Unknown"),
                ext.get("primary_barrier", "Unknown"),
                ext.get("intensity", 5),
                ext.get("user_segment", "General")
            ))
            conn.commit()
            
    def get_unprocessed_comments(self):
        """
        Returns comments that have not been processed by the LLM yet.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.text, c.cluster_id FROM comments c
                LEFT JOIN extractions e ON c.id = e.comment_id
                WHERE e.comment_id IS NULL
            """)
            return cursor.fetchall()
            
    def get_extraction_summary(self):
        """
        Analytical helper to return aggregated counts of barriers and segments.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT primary_barrier, count(*) as freq, avg(intensity) as avg_int
                FROM extractions
                GROUP BY primary_barrier
                ORDER BY freq DESC
            """)
            return cursor.fetchall()
