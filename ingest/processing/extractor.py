import logging
import requests
import json
from ingest import config

logger = logging.getLogger(__name__)

class GroqExtractor:
    """
    Interfaces with the Groq API to extract structured purchase barriers,
    motivations, intent intensity, and user segments from reviews.
    """
    def __init__(self, api_key=None, model="llama-3.1-8b-instant"):
        self.api_key = api_key or config.GROQ_API_KEY
        self.model = model
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        
        self.has_key = bool(self.api_key and self.api_key != "your_groq_api_key_here")
        if not self.has_key:
            logger.warning("No valid Groq API key found in .env. Extractor will run in heuristic fallback mode.")

    def extract(self, text):
        """
        Extracts structured JSON data. Uses API if available, else falls back to heuristics.
        """
        if not self.has_key:
            return self._heuristic_fallback(text)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        system_prompt = """
        You are a customer research AI that analyzes user feedback regarding wishlisted products.
        Analyze the comment and return a JSON object with the following fields:
        {
          "motivation": "A brief string representing the user's primary reason for saving the product (e.g., waiting for sale, bookmarking, birthday occasion)",
          "primary_barrier": "The primary roadblock preventing the purchase. Must be one of: [Price Uncertainty, Fit or Size Concerns, Out of Stock, High Price, Shipping Cost, Insufficient Reviews, Need Verification]",
          "intensity": An integer from 1 to 10 representing the severity/urgency of the roadblock (1 = minor, 10 = absolute dealbreaker),
          "user_segment": "The buyer segment. Must be one of: [Budget Conscious, Sizing Anxious, Brand Fanatic, Occasion Shopper, Window Shopper]"
        }
        Do not output any markdown formatting, thoughts, or explanations. Return raw JSON only.
        """

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Review Text: {text}"}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            res_json = response.json()
            content = res_json["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            logger.error(f"Groq API extraction failed: {e}. Falling back to heuristics.")
            return self._heuristic_fallback(text)

    def _heuristic_fallback(self, text):
        """
        Heuristic fallback model to analyze comments when Groq API is unavailable.
        """
        text_lower = text.lower()
        
        # Defaults
        motivation = "Bookmarking"
        primary_barrier = "Need Verification"
        intensity = 5
        user_segment = "Window Shopper"

        # Sizing / Fit
        if "size" in text_lower or "fit" in text_lower or "fits" in text_lower:
            motivation = "Occasion purchase consideration"
            primary_barrier = "Fit or Size Concerns"
            intensity = 8
            user_segment = "Sizing Anxious"
        
        # Out of Stock
        elif "stock" in text_lower or "sold out" in text_lower:
            motivation = "Sale price tracking"
            primary_barrier = "Out of Stock"
            intensity = 9
            user_segment = "Occasion Shopper"

        # Price / Sale / Expensive
        elif "price" in text_lower or "sale" in text_lower or "cost" in text_lower or "expensive" in text_lower or "inr" in text_lower or "charge" in text_lower:
            motivation = "Waiting for discounts"
            primary_barrier = "Price Uncertainty"
            if "shipping" in text_lower or "delivery" in text_lower:
                primary_barrier = "Shipping Cost"
            intensity = 7
            user_segment = "Budget Conscious"
            
        # Quality / Reviews
        elif "quality" in text_lower or "cheap" in text_lower or "reviews" in text_lower or "scared" in text_lower:
            motivation = "Quality inspection"
            primary_barrier = "Insufficient Reviews"
            intensity = 6
            user_segment = "Window Shopper"

        return {
            "motivation": motivation,
            "primary_barrier": primary_barrier,
            "intensity": intensity,
            "user_segment": user_segment
        }
