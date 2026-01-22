"""Category image mapping service."""

from pathlib import Path
from typing import Optional

# Media directory path
MEDIA_DIR = Path("/home/lord/Projects/Rag_Agent/media")

# Category and sub-category to image mapping
# Priority: Sub-category first (more specific), then main category (fallback)
CATEGORY_IMAGE_MAP = {
    # Sub-categories (higher priority - more specific)
    "beads": "micro & nano beads catogary.jpeg",
    "pliers": "Extension pilers Catogary.jpeg",
    "irons": "Extension Irons catogary.jpeg",
    "machines": "Extension 6D machine Catogary.jpeg",
    "glue": "keratun glue catogary .jpeg",
    "needles": None,  # No image available
    "other": None,  # No image for "other" sub-category
    # Main categories (fallback)
    "extension tools": "Hair Extension Tools Catogary.jpeg",
    "human hair bundles": "human hair price.jpeg",
}


def get_category_image(
    categories: list[str], sub_categories: list[str]
) -> Optional[str]:
    """
    Get the most relevant category image based on detected categories.

    Priority: sub_category > category (more specific wins)

    Args:
        categories: List of main categories found in search results
        sub_categories: List of sub-categories found in search results

    Returns:
        Image path (e.g., "/media/filename.jpeg") or None if no match
    """
    # Check sub-categories first (more specific)
    for sub_cat in sub_categories:
        key = sub_cat.lower().strip()
        if key in CATEGORY_IMAGE_MAP and CATEGORY_IMAGE_MAP[key]:
            image_file = CATEGORY_IMAGE_MAP[key]
            if (MEDIA_DIR / image_file).exists():
                return f"/media/{image_file}"

    # Fallback to main category
    for cat in categories:
        key = cat.lower().strip()
        if key in CATEGORY_IMAGE_MAP and CATEGORY_IMAGE_MAP[key]:
            image_file = CATEGORY_IMAGE_MAP[key]
            if (MEDIA_DIR / image_file).exists():
                return f"/media/{image_file}"

    return None
