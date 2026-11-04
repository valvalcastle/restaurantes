from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.restaurants import router as restaurants_router
from app.core.config import settings
from app.core.templates import templates
from app.web.views import router as views_router

BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(restaurants_router, prefix="/api/v1")
app.include_router(views_router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.exception_handler(StarletteHTTPException)
async def html_aware_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """La API responde JSON; las páginas HTML muestran una pantalla de error amigable."""
    path = request.url.path
    if path.startswith(("/api", "/health", "/static", "/docs", "/openapi")):
        return await http_exception_handler(request, exc)
    message = "No encontramos esa página." if exc.status_code == 404 else str(exc.detail)
    if exc.status_code == 404 and path.startswith("/restaurants/"):
        message = "Ese restaurante no existe o ya fue eliminado."
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": exc.status_code, "message": message},
        status_code=exc.status_code,
    )
