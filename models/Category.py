from dataclasses import dataclass
from models import Model


@dataclass
class Category(Model):
    """Model of a RuneScape item category_id."""

    id: int
    name: str
    item_count: int
