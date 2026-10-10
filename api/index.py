import pandas as pd
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Solar Inverter API")

ROOT = Path(__file__).resolve().parent.parent
EXCEL_FILE = ROOT / "data" / "inverters.xlsx"

def clean(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def price(value):
    try:
        if pd.isna(value) or value == "":
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

def load_products():
    df = pd.read_excel(EXCEL_FILE)
    products = []
    for i, row in df.iterrows():
        products.append({
            "id": i + 1,
            "product_name": clean(row.get("Product Name", "")),
            "brand": clean(row.get("Brand", "")),
            "model": clean(row.get("Model", "")),
            "current_price": price(row.get("Current Price (PKR)")),
            "original_price": price(row.get("Original Price (PKR)")),
            "product_url": clean(row.get("Product URL", "")),
            "image_url": clean(row.get("Image URL", "")),
            "description": clean(row.get("Description", "")),
        })
    return products

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/inverters")
def list_inverters(
    q: str = Query(default="", max_length=200),
    brand: str = Query(default="", max_length=200),
):
    products = load_products()
    if q.strip():
        term = q.strip().casefold()
        products = [
            p for p in products
            if term in p["product_name"].casefold()
            or term in p["brand"].casefold()
            or term in p["model"].casefold()
        ]
    if brand.strip():
        products = [
            p for p in products
            if p["brand"].casefold() == brand.strip().casefold()
        ]
    return {"total": len(products), "products": products}

@app.get("/api/inverters/{product_id}")
def get_inverter(product_id: int):
    products = load_products()
    for product in products:
        if product["id"] == product_id:
            return product
    return {"detail": "Inverter not found"}

app.mount("/", StaticFiles(directory=str(ROOT / "public"), html=True), name="frontend")
