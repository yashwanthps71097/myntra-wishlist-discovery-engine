# Prompt Tuner & Model Refinement Guide

This document outlines how to refine and fine-tune the LLM extraction taxonomy and prompts in the **AI Discovery Engine** based on user interview feedback (as part of Phase 5).

---

## 1. Modifying the Extraction Taxonomy

All structured categories are defined inside [**`ingest/processing/extractor.py`**](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/AI%20Discovered%20Engine/ingest/processing/extractor.py).

If your user interviews reveal a new purchase roadblock (e.g. *Payment Gateway Issues* or *Coupon Misunderstandings*), update the model guidelines:

### Step 1: Update system instructions
Open [`extractor.py`](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/AI%20Discovered%20Engine/ingest/processing/extractor.py#L30-L38) and edit the system prompt block to append your new categories:

```python
system_prompt = """
...
"primary_barrier": "Must be one of: [Price Uncertainty, Fit or Size Concerns, Out of Stock, High Price, Shipping Cost, Insufficient Reviews, Need Verification, NEW_CATEGORY_HERE]",
...
"""
```

### Step 2: Update database heuristics fallback
If you want the pipeline to process local mock data or handle API errors gracefully, update the heuristic fallback method [`_heuristic_fallback(text)`](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/AI%20Discovered%20Engine/ingest/processing/extractor.py#L67-L100) to map new keywords:

```python
elif "keyword_here" in text_lower:
    primary_barrier = "NEW_CATEGORY_HERE"
```

---

## 2. Refining Prompt Instructions (Few-Shot Prompting)

If the LLM frequently misclassifies comment sentiments or intensities:
1. Open [`extractor.py`](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/AI%20Discovered%20Engine/ingest/processing/extractor.py).
2. Inject few-shot examples into the `messages` array payload to enforce strict formatting:

```python
"messages": [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Review Text: I wishlisted this dress but size is not available"},
    {"role": "assistant", "content": '{"motivation": "Occasion buy", "primary_barrier": "Out of Stock", "intensity": 9, "user_segment": "Occasion Shopper"}'},
    {"role": "user", "content": f"Review Text: {text}"}
]
```

---

## 3. Business Impact Weight Tuning

If product priorities change, edit the opportunity scoring weights in [**`app.py`**](file:///c:/Users/ADMIN/Desktop/Product%20Owner%20Project%202/AI%20Discovered%20Engine/app.py):

```python
BARRIER_IMPACT_WEIGHTS = {
    "Price Uncertainty": 0.9,
    "Fit or Size Concerns": 0.8,
    "Out of Stock": 0.9,
    "Insufficient Reviews": 0.6,
    "Shipping Cost": 0.7,
    "Need Verification": 0.5,
    "NEW_BARRIER": 0.8  # Add custom weight (0.0 to 1.0)
}
```
*Opportunity scores on the dashboard will recalculate automatically.*
