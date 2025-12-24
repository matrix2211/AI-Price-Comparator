from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from ai import build_group_response
from providers import search_products
from ai import group_products, pick_best, generate_verdict

app = FastAPI()

# Serve static assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Homepage
@app.get("/")
def home():
    return FileResponse("static/index.html")

# API endpoint
@app.get("/compare")
def compare(query: str):
    raw_products = search_products(query)

    groups = group_products(raw_products)
    response = [build_group_response(g) for g in groups]


    for group in groups:
        best = pick_best(group["items"])
        verdict = generate_verdict(group["items"])

        response.append({
            "product": best["title"],
            "offers": group["items"],
            "best": best,
            "verdict": verdict
        })

    return response
