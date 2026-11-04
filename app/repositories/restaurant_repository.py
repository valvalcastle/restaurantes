"""Único lugar de la app que habla con Firestore."""
from __future__ import annotations

from google.cloud.firestore import Query
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.firebase import get_db
from app.domain.models import COLLECTION


class RestaurantRepository:
    def __init__(self, db=None):
        self._db = db

    @property
    def collection(self):
        # Resuelto al usarse, no al construirse (más fácil de probar).
        return (self._db or get_db()).collection(COLLECTION)

    @staticmethod
    def _to_dict(doc) -> dict:
        return doc.to_dict() | {"id": doc.id}

    def create(self, data: dict) -> dict:
        ref = self.collection.document()  # ID automático
        document = {**data, "id": ref.id, "avgRating": 0, "numRatings": 0}
        ref.set(document)
        return document

    def get(self, restaurant_id: str) -> dict | None:
        doc = self.collection.document(restaurant_id).get()
        if not doc.exists:
            return None
        return self._to_dict(doc)

    def list(
        self,
        category: str | None = None,
        city: str | None = None,
        price: int | None = None,
        order_by: str = "name",
        limit: int = 20,
        start_after: str | None = None,
    ) -> list[dict]:
        query = self.collection
        if category:
            query = query.where(filter=FieldFilter("category", "==", category))
        if city:
            query = query.where(filter=FieldFilter("city", "==", city))
        if price:
            query = query.where(filter=FieldFilter("price", "==", price))

        # Nombre A-Z; calificación de mayor a menor.
        direction = Query.DESCENDING if order_by == "avgRating" else Query.ASCENDING
        query = query.order_by(order_by, direction=direction).limit(limit)

        if start_after:
            last_doc = self.collection.document(start_after).get()
            if last_doc.exists:
                query = query.start_after(last_doc)

        return [self._to_dict(doc) for doc in query.stream()]

    def facets(self) -> dict[str, list[str]]:
        """Ciudades y categorías existentes (para llenar los filtros)."""
        cities, categories = set(), set()
        for doc in self.collection.select(["city", "category"]).stream():
            data = doc.to_dict()
            if data.get("city"):
                cities.add(data["city"])
            if data.get("category"):
                categories.add(data["category"])
        return {"cities": sorted(cities), "categories": sorted(categories)}

    def update(self, restaurant_id: str, data: dict) -> dict | None:
        ref = self.collection.document(restaurant_id)
        if not ref.get().exists:
            return None
        ref.update(data)
        return self.get(restaurant_id)

    def delete(self, restaurant_id: str) -> bool:
        ref = self.collection.document(restaurant_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True
