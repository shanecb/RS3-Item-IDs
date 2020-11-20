from dataclasses import dataclass
from typing import Dict, Any

from models import Model


@dataclass
class Category(Model):
    """Model of a RuneScape item category."""

    id: int
    name: str
    item_count: int