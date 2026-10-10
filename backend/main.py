from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from backend.database import Base, engine, SessionLocal
from backend.models import Inverter

app = FastAPI(title="Solar Inverter API", version="1.0.0")

Base.metadata.create_all(bind=engine)

def get_db():
    with SessionLocal() as db:
        yield db

def product_to_dict(product):
    return {
        "id": product.id,
        "product_name": product.product_name,
        "brand": product.brand,
        "model": product.model,
        "current_price": product.current_price,
        "original_price": product.original_price,
        "product_url": product.product_url,
        "image_url": product.image_url,
        "description": product.description,
    }

@app.get("/health")
def health():
    return {"status": "ok", "message": "Inverter backend is running"}

@app.get("/api/inverters")
def list_inverters(
    q: str = Query(default="", max_length=200),
    brand: str = Query(default="", max_length=200),
    db: Session = Depends(get_db),
):
    statement = select(Inverter)

    if q.strip():
        search = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Inverter.product_name.ilike(search),
                Inverter.brand.ilike(search),
                Inverter.model.ilike(search),
            )
        )

    if brand.strip():
        statement = statement.where(Inverter.brand.ilike(brand.strip()))

    products = db.scalars(statement.order_by(Inverter.id)).all()

    return {
        "total": len(products),
        "products": [product_to_dict(p) for p in products],
    }

@app.get("/api/inverters/{product_id}")
def get_inverter(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Inverter, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Inverter not found")
    return product_to_dict(product)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
