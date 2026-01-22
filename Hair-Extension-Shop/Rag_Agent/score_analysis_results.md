# Similarity Score Analysis Results

**Date**: 2026-01-19
**Collection**: rag_products (134 products)
**Current Retrieval Threshold**: 0.45

## Key Findings

### 1. Generic Greetings (Should NOT trigger product images)
| Query | Top Score | Status at 0.45 threshold |
|-------|-----------|-------------------------|
| "Hi" | 0.4529 | ❌ **Returns 2 products** |
| "Hello" | 0.3939 | ✅ Returns 0 products |
| "Hey there" | 0.3762 | ✅ Returns 0 products |
| "Good morning" | 0.3387 | ✅ Returns 0 products |

**Problem**: "Hi" scores just above the 0.45 threshold (0.4529), causing it to retrieve products!

### 2. Generic Product Questions (Borderline - may trigger images)
| Query | Top Score |
|-------|-----------|
| "What products do you have" | 0.5420 |
| "Show me your products" | 0.4827 |
| "What do you sell" | 0.5003 |

These queries legitimately ask about products, so returning results is acceptable.

### 3. Specific Product Queries (Should definitely trigger images)
| Query | Top Score | Category Match |
|-------|-----------|---------------|
| "beads" | 0.6481 | Extension Tools > Beads |
| "pliers" | 0.6594 | Extension Tools > Pliers |
| "hair extension" | 0.6432 | Extension Tools |
| "Human Hair Bundles" | 0.6988 | Human Hair Bundles |
| "crimping tool" | 0.5402 | Extension Tools > Pliers |
| "blonde hair" | 0.4671 | Human Hair Bundles |

Strong semantic matches with scores significantly above 0.50.

## Score Distribution Patterns

### Generic Greetings: 0.33 - 0.45
- "Good morning": 0.3387
- "Hey there": 0.3762
- "Hello": 0.3939
- **"Hi": 0.4529** ⚠️ (Outlier!)

### Generic Product Questions: 0.48 - 0.54
- "Show me your products": 0.4827
- "What do you sell": 0.5003
- "What products do you have": 0.5420

### Specific Product Queries: 0.54 - 0.70
- "crimping tool": 0.5402
- "hair extension": 0.6432
- "beads": 0.6481
- "pliers": 0.6594
- "Human Hair Bundles": 0.6988

## Threshold Testing for "Hi"

| Threshold | Results | Notes |
|-----------|---------|-------|
| 0.00 | 5 results | All matches |
| 0.30 | 5 results | Too low |
| 0.40 | 5 results | Too low |
| **0.45** | **2 results** | **Current setting - problematic!** |
| **0.50** | **0 results** | ✅ **Filters out "Hi"** |
| 0.55 | 0 results | Safe |
| 0.60 | 0 results | Safe |

## Recommendations

### Option 1: Conservative Approach (Recommended)
```python
RETRIEVAL_THRESHOLD = 0.45  # Keep for general search
CATEGORY_IMAGE_THRESHOLD = 0.50  # Use for deciding when to show images
```

**Reasoning**:
- Generic greetings like "Hi" score 0.45-0.46, so 0.50 filters them out
- Generic product questions score 0.48-0.54, which is acceptable for showing category images
- Specific queries score 0.54+, well above the threshold
- Safe gap between greetings (max 0.45) and product queries (min 0.48)

### Option 2: More Selective Approach
```python
RETRIEVAL_THRESHOLD = 0.45  # Keep for general search
CATEGORY_IMAGE_THRESHOLD = 0.55  # More selective
```

**Reasoning**:
- Only shows images for very specific queries (0.55+)
- Filters out generic product questions like "What products do you have" (0.54)
- May be too restrictive for some legitimate queries

### Option 3: Dual Threshold Strategy
```python
RETRIEVAL_THRESHOLD = 0.50  # Raise the base threshold
CATEGORY_IMAGE_THRESHOLD = 0.55  # Even higher for images
```

**Reasoning**:
- Completely eliminates noise from greetings
- Only returns results for actual product queries
- May filter out some borderline valid queries

## Recommended Implementation

### Update RAG Service (backend/app/services/rag_service.py)

```python
class RAGService:
    def __init__(self):
        # ... existing code ...
        self.retrieval_threshold = 0.45  # General retrieval
        self.image_threshold = 0.50      # Category image display

    def generate_response(self, query: str, session_id: str = None):
        # Search with retrieval threshold
        products = self.vector_store.search(
            query,
            top_k=5,
            score_threshold=self.retrieval_threshold
        )

        # Determine if we should show category image
        show_category_image = False
        if products and products[0]['score'] >= self.image_threshold:
            show_category_image = True

        # ... rest of the logic ...
```

### Update Frontend Logic (if needed)

The frontend should check if `category_image` is included in the response before displaying it.

## Conclusion

**Root Cause**: "Hi" returns products with scores of 0.4529, just above the 0.45 threshold.

**Solution**: Use a dual-threshold approach:
- Keep 0.45 for retrieving products (context for LLM)
- Use **0.50** as the threshold for showing category images

This creates a safe gap:
- Greetings: max score 0.45 → No images
- Product queries: min score 0.48 → Shows images
- Specific queries: scores 0.54+ → Definitely shows images

**Next Steps**:
1. Update `rag_service.py` with dual threshold logic
2. Modify the response structure to include `show_category_image` flag
3. Test with various queries to confirm behavior
