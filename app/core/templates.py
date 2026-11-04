from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.domain.models import PRICE_LABELS

BASE_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
templates.env.filters["price_label"] = lambda value: PRICE_LABELS.get(value, "?")
