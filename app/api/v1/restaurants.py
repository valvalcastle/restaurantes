from fastapi import APIRouter, Depends, Query, Response

from app.api.deps import get_service
from app.domain.schemas import (
    OrderBy,
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
)
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

# Nota: son funciones "def" (no "async def") porque el cliente de Firestore es
# síncrono; así FastAPI las ejecuta en un hilo y no bloquea el servidor.


@router.get("", response_model=list[RestaurantResponse])
def list_restaurants(
    response: Response,
    category: str | None = None,
    city: str | None = None,
    price: int | None = Query(default=None, ge=1, le=3),
    order_by: OrderBy = "name",
    limit: int = Query(default=20, ge=1, le=100),
    start_after: str | None = None,
    service: RestaurantService = Depends(get_service),
):
    items = service.list(
        category=category,
        city=city,
        price=price,
        order_by=order_by,
        limit=limit,
        start_after=start_after,
    )
    # Paginación: si la página vino llena, el ID del último sirve de cursor.
    if len(items) == limit:
        response.headers["X-Next-Cursor"] = items[-1]["id"]
    return items


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: str, service: RestaurantService = Depends(get_service)):
    return service.get(restaurant_id)


@router.post("", status_code=201, response_model=RestaurantResponse)
def create_restaurant(
    payload: RestaurantCreate, service: RestaurantService = Depends(get_service)
):
    return service.create(payload)


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: str,
    payload: RestaurantUpdate,
    service: RestaurantService = Depends(get_service),
):
    return service.update(restaurant_id, payload)


@router.delete("/{restaurant_id}", status_code=204)
def delete_restaurant(restaurant_id: str, service: RestaurantService = Depends(get_service)):
    service.delete(restaurant_id)
    return Response(status_code=204)
