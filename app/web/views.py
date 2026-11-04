"""Vistas HTML (Jinja2). Los datos se modifican desde app.js llamando a /api/v1."""
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api.deps import get_service
from app.core.templates import templates
from app.services.restaurant_service import RestaurantService

router = APIRouter(include_in_schema=False)

PAGE_SIZE = 20

FLASH_MESSAGES = {
    "created": "Restaurante creado correctamente.",
    "updated": "Cambios guardados.",
    "deleted": "Restaurante eliminado.",
}


def _text(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def _price(value: str | None) -> int | None:
    value = (value or "").strip()
    return int(value) if value in ("1", "2", "3") else None


@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    category: str | None = None,
    city: str | None = None,
    price: str | None = None,
    order_by: str = "name",
    start_after: str | None = None,
    msg: str | None = None,
    service: RestaurantService = Depends(get_service),
):
    # Los <select> del formulario envían "" cuando eligen "Todas": se normaliza.
    filters = {
        "category": _text(category),
        "city": _text(city),
        "price": _price(price),
        "order_by": order_by if order_by in ("name", "avgRating") else "name",
    }
    restaurants = service.list(**filters, limit=PAGE_SIZE, start_after=_text(start_after))
    facets = service.facets()

    next_url = None
    if len(restaurants) == PAGE_SIZE:
        params = {k: v for k, v in filters.items() if v is not None}
        params["start_after"] = restaurants[-1]["id"]
        next_url = "/?" + urlencode(params)

    return templates.TemplateResponse(
        request,
        "restaurants.html",
        {
            "restaurants": restaurants,
            "cities": facets["cities"],
            "categories": facets["categories"],
            "filters": filters,
            "has_filters": any(filters[k] for k in ("category", "city", "price")),
            "next_url": next_url,
            "flash": FLASH_MESSAGES.get(msg or ""),
        },
    )


@router.get("/restaurants")
def restaurants_redirect():
    return RedirectResponse("/")


# /new debe declararse antes que /{restaurant_id}, o "new" se tomaría como un ID.
@router.get("/restaurants/new", response_class=HTMLResponse)
def new_restaurant_form(request: Request):
    return templates.TemplateResponse(request, "restaurant_form.html", {"restaurant": None})


@router.get("/restaurants/{restaurant_id}", response_class=HTMLResponse)
def restaurant_detail(
    request: Request,
    restaurant_id: str,
    msg: str | None = None,
    service: RestaurantService = Depends(get_service),
):
    restaurant = service.get(restaurant_id)  # 404 si no existe
    return templates.TemplateResponse(
        request,
        "restaurant_detail.html",
        {"restaurant": restaurant, "flash": FLASH_MESSAGES.get(msg or "")},
    )


@router.get("/restaurants/{restaurant_id}/edit", response_class=HTMLResponse)
def edit_restaurant_form(
    request: Request,
    restaurant_id: str,
    service: RestaurantService = Depends(get_service),
):
    restaurant = service.get(restaurant_id)
    return templates.TemplateResponse(
        request, "restaurant_form.html", {"restaurant": restaurant}
    )
