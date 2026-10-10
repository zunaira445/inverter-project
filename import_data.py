import pandas as pd
from sqlalchemy import select
from backend.database import Base, engine, SessionLocal
from backend.models import Inverter

EXCEL_FILE = "data/inverters.xlsx"

def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()

def clean_price(value):
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def main():
    df = pd.read_excel(EXCEL_FILE)
    df.columns = df.columns.str.strip()

    required = [
        "Product Name", "Brand", "Model",
        "Current Price (PKR)", "Original Price (PKR)",
        "Product URL", "Image URL", "Description"
    ]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Excel mein required columns missing hain: {missing}")

    Base.metadata.create_all(bind=engine)
    added = 0
    updated = 0
    skipped = 0

    with SessionLocal() as session:
        for _, row in df.iterrows():
            product_url = clean_text(row["Product URL"])
            product_name = clean_text(row["Product Name"])

            if not product_url or not product_name:
                skipped += 1
                continue

            product = session.scalar(
                select(Inverter).where(Inverter.product_url == product_url)
            )

            if product is None:
                product = Inverter(
                    product_name=product_name,
                    product_url=product_url
                )
                session.add(product)
                added += 1
            else:
                updated += 1

            product.product_name = product_name
            product.brand = clean_text(row["Brand"])
            product.model = clean_text(row["Model"])
            product.current_price = clean_price(row["Current Price (PKR)"])
            product.original_price = clean_price(row["Original Price (PKR)"])
            product.image_url = clean_text(row["Image URL"])
            product.description = clean_text(row["Description"])

        session.commit()
        total = len(session.scalars(select(Inverter)).all())

    print(f"Excel rows: {len(df)}")
    print(f"New products: {added}")
    print(f"Updated products: {updated}")
    print(f"Skipped rows: {skipped}")
    print(f"Total products in database: {total}")

if __name__ == "__main__":
    main()
