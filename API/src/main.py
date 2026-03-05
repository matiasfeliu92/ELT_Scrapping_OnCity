from fastapi import FastAPI

from API.src.products.infrastructure.api.product_routes import products_router

def create_app() -> FastAPI:
    app = FastAPI(title="Products App", version="1.0.0")
    app.include_router(products_router, tags=["products"])
    return app

app = create_app()

@app.get("/")
def get_root():
    return "hello world"