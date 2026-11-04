from app.services.restaurant_service import RestaurantService


def get_service() -> RestaurantService:
    """Dependencia inyectable (las pruebas la reemplazan con un Firestore falso)."""
    return RestaurantService()
