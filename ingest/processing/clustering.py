import logging
import numpy as np
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

class FeedbackClustering:
    """
    Groups feedback embeddings into semantic categories.
    Uses HDBSCAN as default, and falls back to KMeans if data size is too small
    or if HDBSCAN yields only noise (-1).
    """
    def __init__(self, min_cluster_size=2):
        self.min_cluster_size = min_cluster_size

    def fit_predict(self, embeddings, texts):
        if len(embeddings) < self.min_cluster_size:
            logger.warning("Not enough samples to cluster. Assigning all to single default cluster.")
            return [0] * len(embeddings), {0: ["General / Small Dataset"]}
        
        X = np.array(embeddings)
        
        # Try HDBSCAN (since scikit-learn >= 1.3.0 includes it natively)
        try:
            logger.info("Fitting HDBSCAN clustering...")
            hdb = HDBSCAN(min_cluster_size=self.min_cluster_size, min_samples=1)
            labels = hdb.fit_predict(X).tolist()
            
            # Check if HDBSCAN classed everything as noise (-1)
            unique_labels = set(labels)
            if len(unique_labels) == 1 and -1 in unique_labels:
                logger.info("HDBSCAN categorized all items as noise. Falling back to KMeans...")
                labels = self._run_kmeans_fallback(X)
        except Exception as e:
            logger.error(f"HDBSCAN failed: {e}. Falling back to KMeans...")
            labels = self._run_kmeans_fallback(X)
            
        # Post-process outlier noise (-1) to a standard group name
        # If HDBSCAN output has -1, it means "Unclassified/Noise"
        
        # Calculate cluster keywords using TF-IDF
        keywords_map = self._extract_cluster_keywords(labels, texts)
        
        return labels, keywords_map

    def _run_kmeans_fallback(self, X):
        # Dynamically set clusters depending on data size
        n_samples = X.shape[0]
        n_clusters = min(3, n_samples)
        logger.info(f"Running KMeans with {n_clusters} clusters...")
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        return km.fit_predict(X).tolist()

    def _extract_cluster_keywords(self, labels, texts, num_keywords=3):
        """
        Uses TF-IDF to find top defining words for each cluster label.
        """
        keywords_map = {}
        unique_labels = set(labels)
        
        # Prepare text lists for each cluster
        cluster_docs = {}
        for label in unique_labels:
            cluster_docs[label] = []
            
        for label, text in zip(labels, texts):
            cluster_docs[label].append(text)
            
        for label, docs in cluster_docs.items():
            if label == -1:
                keywords_map[label] = ["Outliers", "Miscellaneous"]
                continue
                
            combined_text = " ".join(docs)
            if not combined_text.strip():
                keywords_map[label] = ["Empty"]
                continue
                
            try:
                # Basic TF-IDF on this cluster's text
                vectorizer = TfidfVectorizer(stop_words='english', max_features=10)
                tfidf_matrix = vectorizer.fit_transform(docs)
                feature_names = vectorizer.get_feature_names_out()
                
                # Sum tfidf weights for each term across all docs in the cluster
                sums = tfidf_matrix.sum(axis=0).A1
                data = list(zip(feature_names, sums))
                # Sort descending
                data.sort(key=lambda x: x[1], reverse=True)
                
                keywords = [word for word, score in data[:num_keywords]]
                keywords_map[label] = keywords if keywords else ["Feedback"]
            except Exception:
                # Fallback simple keyword extraction if vectorizer fails on short/empty text
                words = [w.lower() for w in combined_text.split() if len(w) > 4]
                keywords_map[label] = list(set(words))[:num_keywords] if words else ["General"]
                
        return keywords_map
