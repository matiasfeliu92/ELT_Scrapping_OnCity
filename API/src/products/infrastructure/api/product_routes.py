from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from API.src.products.application.services.product_service import ProductService
from API.src.products.domain.exceptions import ProductNotFoundError
from API.src.db.config import Config
from API.src.products.infrastructure.repositories.sqlalchemy_product_repository import SQLAlchemyProductRepository
from API.src.products.infrastructure.schemas.product import Product as ProductResponse

products_router = APIRouter(prefix="/v1/products")
config = Config()
get_db = config.get_db

@products_router.get("/", response_model=List[ProductResponse])
def list_users(db: Session = Depends(get_db)):
    repo = SQLAlchemyProductRepository(db)
    service = ProductService(repo)
    products = service.get_all()
    return [ProductResponse.model_validate(p) for p in products]

@products_router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    repo = SQLAlchemyProductRepository(db)
    service = ProductService(repo)
    try:
        product = service.get_one_by_id(product_id)
        return ProductResponse.model_validate(product)
    except ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")