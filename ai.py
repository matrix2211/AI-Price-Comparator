import re
import requests
import numpy as np
from variant_agent import analyze_variants

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text"

# ---------- In-memory embedding cache ----------
_embedding_cache: dict[str, list[float]] = {}

# ---------- Verdict cache ----------
_verdict_cache = {}


# ---------- Utilities ----------
def cosine(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def extract_signature(title: str):
    t = title.lower()

    model = re.search(r"iphone\s*(\d+)", t)
    storage = re.search(r"(\d+)\s*gb", t)

    if "pro max" in t:
        variant = "pro max"
    elif "pro" in t:
        variant = "pro"
    elif "plus" in t:
        variant = "plus"
    else:
        variant = "base"

    return {
        "model": model.group(1) if model else None,
        "variant": variant,
        "storage": storage.group(1) if storage else None
    }


def same_variant(a, b):
    if a["model"] != b["model"]:
        return False
    if a["variant"] != b["variant"]:
        return False
    if a["storage"] and b["storage"] and a["storage"] != b["storage"]:
        return False
    return True


# ---------- Batch embeddings ----------
def batch_embed(texts: list[str]) -> dict[str, list[float]]:
    """
    Returns embeddings for all texts using:
    - cache first
    - single Ollama call per text (Ollama limitation)
    """
    embeddings = {}

    for text in texts:
        if text in _embedding_cache:
            embeddings[text] = _embedding_cache[text]
            continue

        res = requests.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": text},
            timeout=15
        )
        emb = res.json()["embedding"]
        _embedding_cache[text] = emb
        embeddings[text] = emb

    return embeddings


# ---------- Grouping ----------
def group_products(products, threshold=0.86):
    # hard limit for performance
    products = products[:8]

    titles = list({p["title"] for p in products})
    embeddings = batch_embed(titles)

    groups = []

    for product in products:
        title = product["title"]
        sig = extract_signature(title)
        emb = embeddings.get(title)

        if emb is None:
            continue

        placed = False

        for group in groups:
            if not same_variant(sig, group["signature"]):
                continue

            sim = cosine(emb, group["embedding"])
            if sim >= threshold:
                group["items"].append(product)
                placed = True
                break

        if not placed:
            groups.append({
                "embedding": emb,
                "signature": sig,
                "items": [product]
            })

    # cleanup internal keys
    for g in groups:
        del g["embedding"]
        del g["signature"]

    return groups


# ---------- Best offer ----------
def pick_best(products):
    return min(products, key=lambda x: x["price"])


# ---------- Verdict generation ----------
def generate_verdict(offers):
    """
    Generate a short, human-readable verdict explaining why this is the best deal.
    Cached for performance.
    """
    key = tuple(sorted((o["source"], o["price"]) for o in offers))
    if key in _verdict_cache:
        return _verdict_cache[key]

    cheapest = min(offers, key=lambda x: x["price"])
    prices = sorted(o["price"] for o in offers)

    if len(prices) == 1:
        verdict = (
            f"Only one seller available: {cheapest['source']} "
            f"at ₹{cheapest['price']}."
        )
    else:
        diff = prices[1] - prices[0]
        verdict = (
            f"{cheapest['source']} offers the best price at ₹{cheapest['price']}, "
            f"₹{diff} cheaper than the next option."
        )

    _verdict_cache[key] = verdict
    return verdict


# ---------- Variant AI integration (NEW) ----------
def enrich_group_with_variants(group_items):
    """
    Adds AI-driven variant insight to a grouped product.
    Safe, additive, no side effects.
    """
    try:
        return analyze_variants(
            product_name=group_items[0]["title"],
            offers=group_items
        )
    except Exception:
        # Never let AI logic break the pipeline
        return None


# ---------- Final group response builder (NEW) ----------
def build_group_response(group):
    """
    Builds the final response object for ONE grouped product.
    This keeps main.py clean and stable.
    """
    offers = group["items"]
    best = pick_best(offers)
    verdict = generate_verdict(offers)

    response = {
        "product": best["title"],
        "offers": offers,
        "best": best,
        "verdict": verdict
    }

    variant_insight = enrich_group_with_variants(offers)
    if variant_insight:
        response["variant_insight"] = variant_insight

    return response
