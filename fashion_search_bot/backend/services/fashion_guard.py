FASHION_KEYWORDS = [
    "dress", "shirt", "top", "kurti", "saree", "lehenga",
    "jeans", "trousers", "pants", "skirt", "gown",
    "jacket", "coat", "sweater", "hoodie", "blazer",
    "fabric", "cotton", "silk", "linen", "denim",
    "embroidered", "printed", "outfit", "apparel", "clothing"
]

def is_fashion_item(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in FASHION_KEYWORDS)
