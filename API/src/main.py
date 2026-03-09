from fastapi import FastAPI

from API.src.auth.infrastructure.api.auth_routes import auth_router
from API.src.products.infrastructure.api.product_routes import products_router
from API.src.users.infrastructure.api.user_routes import user_router
from API.src.shared.infrastructure.db.config import Config

def create_app() -> FastAPI:
    app = FastAPI(title="Products App", version="1.0.0")
    app.include_router(auth_router, tags=["auth"])
    app.include_router(products_router, tags=["products"])
    app.include_router(user_router, tags=["users"])
    return app

app = create_app()
Config().create_tables()

@app.get("/")
def get_root():
    return "hello world"