import re
from collections import defaultdict

STORAGE_RE = re.compile(r"(64|128|256|512|1024)\s?GB", re.I)

def extract_storage(title: str):
    m = STORAGE_RE.search(title)
    if not m:
        return None
    return int(m.group(1))

def analyze_variants(product_name: str, offers: list):
    """
    Deterministic variant analysis + reasoning.
    No scraping, no IO, no side effects.
    """

    variants = defaultdict(list)

    for o in offers:
        storage = extract_storage(o["title"])
        if storage:
            variants[storage].append(o)

    if not variants:
        return None

    summary = {}
    for storage, items in variants.items():
        summary[f"{storage}GB"] = {
            "min_price": min(i["price"] for i in items),
            "count": len(items)
        }

    # sort variants by storage
    sorted_variants = sorted(summary.items(), key=lambda x: int(x[0].replace("GB", "")))

    # decide best value variant
    best_variant = sorted_variants[0][0]
    best_score = None

    for i in range(1, len(sorted_variants)):
        prev_storage = int(sorted_variants[i-1][0].replace("GB", ""))
        curr_storage = int(sorted_variants[i][0].replace("GB", ""))

        prev_price = sorted_variants[i-1][1]["min_price"]
        curr_price = sorted_variants[i][1]["min_price"]

        storage_gain = curr_storage / prev_storage
        price_gain = curr_price / prev_price

        score = storage_gain / price_gain

        if best_score is None or score > best_score:
            best_score = score
            best_variant = sorted_variants[i][0]

    reasoning = generate_reasoning(sorted_variants, best_variant)

    return {
        "variants": summary,
        "best_variant": best_variant,
        "reasoning": reasoning
    }

def generate_reasoning(sorted_variants, best_variant):
    if len(sorted_variants) < 2:
        return f"{best_variant} is the only available variant."

    texts = []
    for v, data in sorted_variants:
        texts.append(f"{v} at ₹{data['min_price']}")

    joined = ", ".join(texts)

    return (
        f"Available variants are {joined}. "
        f"{best_variant} offers the best balance between price and storage."
    )
