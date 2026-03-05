from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, BigInteger
from API.src.db.config import Config

class Product(Config().Base):
    __tablename__ = 'products'
    __table_args__ = {"schema": "raw","extend_existing": True} # Importante: tu tabla está en el schema 'raw'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    product_id = Column(String, nullable=False)
    name = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    main_category = Column(String, nullable=True)
    sub_category = Column(String, nullable=True)
    list_price = Column("scraped_list_price", Float, nullable=True)
    cash_price = Column("scraped_cash_price", Float, nullable=True)
    stock_level = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, nullable=False)
    retailer = Column(String, nullable=False)
    link = Column(String, nullable=False)

    def __repr__(self):
        return f"<ProductModel(id={self.id}, product_id={self.product_id}, model={self.model})>"