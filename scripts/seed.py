"""Carga 10 restaurantes de prueba en Firestore (emulador o real).

Uso:  python -m scripts.seed

Usa IDs fijos (seed-01 ... seed-10) con set(), así que puedes ejecutarlo
varias veces sin duplicar datos.
"""
from app.core.config import settings
from app.core.firebase import get_db
from app.domain.models import COLLECTION

IMG = "https://images.unsplash.com/{}?auto=format&fit=crop&w=800&q=60"

RESTAURANTS = [
    ("La Abuela", "Mexicana", "Puebla", 2, "photo-1552566626-52f8b828add9", 4.5, 20),
    ("Pizza Central", "Pizza", "Puebla", 1, "photo-1513104890138-7c749659a591", 4.0, 12),
    ("El Mole Poblano", "Mexicana", "Puebla", 2, "photo-1565299624946-b28f40a0ae38", 4.7, 35),
    ("Mariscos del Puerto", "Mariscos", "Veracruz", 3, "photo-1414235077428-338989a2e8c0", 4.2, 18),
    ("Sushi Kiru", "Japonesa", "Ciudad de México", 3, "photo-1540189549336-e6e99c3679fe", 4.6, 41),
    ("Tacos Don Beto", "Tacos", "Puebla", 1, "photo-1555396273-367ea4eb4db5", 4.3, 27),
    ("Trattoria Bella", "Italiana", "Ciudad de México", 3, "photo-1476224203421-9ac39bcb3327", 4.4, 22),
    ("Café La Esquina", "Cafetería", "Cholula", 1, "photo-1517248135467-4c7edcad34c4", 3.9, 9),
    ("Parrilla 54", "Carnes", "Monterrey", 3, "photo-1504674900247-0877df9cc836", 4.1, 15),
    ("Verde Vivo", "Vegetariana", "Cholula", 2, "photo-1482049016688-2d3e1b311543", 4.8, 30),
]


def main() -> None:
    target = settings.FIRESTORE_EMULATOR_HOST or f"proyecto real '{settings.FIREBASE_PROJECT_ID}'"
    print(f"Cargando datos semilla en: {target}")

    db = get_db()
    for i, (name, category, city, price, photo, rating, count) in enumerate(RESTAURANTS, 1):
        doc_id = f"seed-{i:02d}"
        db.collection(COLLECTION).document(doc_id).set(
            {
                "id": doc_id,
                "name": name,
                "category": category,
                "city": city,
                "price": price,
                "photoUrl": IMG.format(photo),
                "avgRating": rating,
                "numRatings": count,
            }
        )
    print(f"Datos semilla creados: {len(RESTAURANTS)} restaurantes")


if __name__ == "__main__":
    main()
