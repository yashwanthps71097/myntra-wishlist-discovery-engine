import logging
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Generates vector representations for reviews and comments.
    Attempts to use sentence-transformers, but falls back to TF-IDF
    vectors if PyTorch/DLL errors prevent model loading on Windows.
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.use_fallback = False
        self.model_name = model_name
        
        try:
            logger.info(f"Attempting to load local SentenceTransformer model '{self.model_name}'...")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info("SentenceTransformer model loaded successfully.")
        except (ImportError, OSError, Exception) as err:
            logger.warning(
                f"Could not load SentenceTransformers due to env/DLL error ({err}). "
                "Falling back to high-performance TF-IDF vectorizer."
            )
            self.use_fallback = True
            # Setup TF-IDF Vectorizer
            self.model = TfidfVectorizer(
                stop_words='english',
                max_features=128, # Match standard embedding dimensions
                ngram_range=(1, 2)
            )

    def generate(self, texts):
        if not texts:
            return []
        
        cleaned_texts = [str(t) if t is not None else "" for t in texts]
        
        if self.use_fallback:
            logger.info(f"Generating TF-IDF semantic vectors for {len(cleaned_texts)} documents...")
            # Fit and transform input text
            vectors = self.model.fit_transform(cleaned_texts).toarray()
            return vectors.tolist()
        
        logger.info(f"Generating SentenceTransformer embeddings for {len(cleaned_texts)} documents...")
        embeddings = self.model.encode(cleaned_texts, show_progress_bar=False)
        return embeddings.tolist()
