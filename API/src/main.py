from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from API.src.auth.infrastructure.api.auth_routes import auth_router
from API.src.products.infrastructure.api.product_routes import products_router
from API.src.shared.exceptions import AppException, InternalServerError
from API.src.users.infrastructure.api.user_routes import user_router
from API.src.shared.infrastructure.db.config import Config

def create_app() -> FastAPI:
    app = FastAPI(title="Products App", version="1.0.0")

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": str(exc), "status": exc.status_code},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception):
        wrapped = InternalServerError("Error interno del servidor")
        return JSONResponse(
            status_code=wrapped.status_code,
            content={"error": str(wrapped), "status": wrapped.status_code},
        )

    app.include_router(auth_router, tags=["auth"])
    app.include_router(products_router, tags=["products"])
    app.include_router(user_router, tags=["users"])
    return app

app = create_app()
Config().create_tables()

@app.get("/")
def get_root():
    return "hello world"