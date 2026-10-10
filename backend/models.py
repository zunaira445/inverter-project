from sqlalchemy import String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Inverter(Base):
    __tablename__ = "inverters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_name: Mapped[str] = mapped_column(String(500))
    brand: Mapped[str] = mapped_column(String(200), default="")
    model: Mapped[str] = mapped_column(String(300), default="")
    current_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    original_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    product_url: Mapped[str] = mapped_column(Text, unique=True)
    image_url: Mapped[str] = mapped_column(Text, default="")
    description: Mapped[str] = mapped_column(Text, default="")
