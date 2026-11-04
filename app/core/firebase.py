"""Conexión a Firestore (emulador local o proyecto real)."""
import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore

from app.core.config import settings


@lru_cache
def get_db() -> firestore.Client:
    """Crea el cliente una sola vez y solo cuando se necesita.

    Es "perezoso" a propósito: importar la app (por ejemplo en las pruebas)
    no abre ninguna conexión.
    """
    using_emulator = bool(settings.FIRESTORE_EMULATOR_HOST)
    if using_emulator:
        # Debe estar definida ANTES de crear el cliente.
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST

    cred = None
    if settings.FIREBASE_CREDENTIALS_PATH and not using_emulator:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {"projectId": settings.FIREBASE_PROJECT_ID})

    return firestore.Client(
        project=settings.FIREBASE_PROJECT_ID,
        credentials=cred.get_credential() if cred else None,
    )
