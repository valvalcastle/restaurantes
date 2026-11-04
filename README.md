# FriendlyEats FastAPI (Sprint 1)

App para promocionar restaurantes. **Sprint 1:** CRUD completo de restaurantes en
Firestore (emulador local) desde FastAPI, con vistas HTML (Jinja2), filtros, datos
semilla y pruebas. Sin autenticación, reseñas, imágenes subidas ni despliegue
(eso es de sprints posteriores).

## Requisitos

- Python 3.10 o superior
- Node.js 18+ (para Firebase CLI)
- **Java 11+ (JDK)**: el emulador de Firestore lo necesita (`java -version`)
- Firebase CLI: `npm install -g firebase-tools`

## Puesta en marcha (primera vez)

```bash
# 1. Entorno virtual e instalación
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Variables de entorno
cp .env.example .env               # Windows: copy .env.example .env

# 3. Firebase (solo si quieres vincular tu proyecto real; el emulador funciona sin esto)
firebase login
firebase use --add                 # elige tu proyecto; o usa el alias por defecto demo-friendlyeats
```

## Ejecutar (3 terminales, con el entorno virtual activado en las de Python)

```bash
# Terminal 1: emulador de Firestore (UI en http://localhost:4000)
firebase emulators:start --only firestore

# Terminal 2: datos semilla (10 restaurantes; se puede repetir sin duplicar)
python -m scripts.seed

# Terminal 3: la aplicación
uvicorn app.main:app --reload
```

Abre **http://localhost:8000**. Documentación interactiva de la API: http://localhost:8000/docs.
Los datos guardados se ven en el emulador: http://localhost:4000/firestore.

## Pruebas

```bash
pytest -v
```

Las pruebas usan un Firestore **en memoria** (`tests/fake_firestore.py`), así que corren sin
emulador ni internet. Hay además una prueba de integración contra el emulador real:

```bash
# con el emulador corriendo
RUN_EMULATOR_TESTS=1 pytest -v tests/test_emulator_integration.py
```

## Endpoints

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/health` | `{"status": "ok"}` |
| GET | `/api/v1/restaurants` | Lista. Params: `city`, `category`, `price` (1-3), `order_by` (`name`/`avgRating`), `limit` (1-100, def. 20), `start_after` (ID). Si hay más páginas, el header `X-Next-Cursor` trae el ID para la siguiente. |
| POST | `/api/v1/restaurants` | Crea (201). `avgRating` y `numRatings` los pone el servidor en 0. |
| GET | `/api/v1/restaurants/{id}` | Detalle (404 si no existe). |
| PATCH | `/api/v1/restaurants/{id}` | Edita solo `name`, `category`, `city`, `price`, `photoUrl` (otro campo → 422). |
| DELETE | `/api/v1/restaurants/{id}` | Elimina (204 o 404). |

Vistas HTML: `/` (listado + filtros), `/restaurants/new`, `/restaurants/{id}`, `/restaurants/{id}/edit`.

## Arquitectura

```
Navegador ──> Vistas Jinja2 (app/web) ─┐
         └─> API REST (app/api/v1) ────┤
                                       ▼
                         RestaurantService (reglas, 404/400)
                                       ▼
                         RestaurantRepository (ÚNICO acceso a Firestore)
                                       ▼
                         Firestore (emulador en local)
```

- `app/domain`: constantes y esquemas Pydantic (validación de campos, tipos y rangos).
- `app/repositories`: todo el acceso a Firestore, aislado.
- `app/services`: lógica de negocio y errores HTTP.
- `app/api/v1`: rutas JSON. `app/web`: rutas HTML. `app/templates` + `static`: interfaz.

## Decisiones

- **Rutas `def` y no `async def`:** el cliente de Firestore es síncrono; así FastAPI las corre en un hilo y no bloquea el servidor.
- **Cliente de Firestore perezoso** (`get_db()`): importar la app no abre conexiones, lo que permite probar sin emulador.
- **Inyección de dependencias** (`get_service`): las pruebas la reemplazan por un Firestore falso.
- **`extra="forbid"`** en crear/editar: no se puede inyectar `avgRating`, `numRatings` ni `id` desde fuera.
- **Filtros de ciudad/categoría como `<select>`** con los valores existentes: Firestore compara texto exacto (distingue mayúsculas), y así se evitan filtros vacíos por error de tipeo.
- **Datos semilla con ID fijo** (`seed-01`…`seed-10`) usando `set()`: se pueden recargar sin duplicar.
- **`.gitignore`:** `*.json` protege las cuentas de servicio, con excepciones para `package.json`, `firebase.json` y `firestore.indexes.json` (si no, `firebase.json` quedaba fuera de Git).
- **`firestore.rules` en "denegar todo"**: nadie accede directo desde el navegador; todo pasa por FastAPI (Admin SDK). El Sprint 2 las reemplaza con reglas por usuario.
- **`firestore.indexes.json`:** el emulador no exige índices, pero Firestore real sí para combinar filtros con orden. Ya están definidos los 14 necesarios (`firebase deploy --only firestore:indexes`).

## Seguridad

Nunca subas a Git la cuenta de servicio (`secrets/service-account.json`) ni tu `.env`. Contra el emulador no se necesita ninguna credencial.

## Estado de las tareas

S1-01 a S1-25 cubiertas. Pendiente de tu parte (requiere tu cuenta): **S1-06**, crear el proyecto en la consola de Firebase y ejecutar `firebase use --add`.

## Próximo sprint

Firebase Authentication, control de propietario con `ownerId`, Security Rules y reseñas con transacciones.
