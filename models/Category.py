from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

from models import Model, DBCategory


@dataclass
class Category(Model):
    """Model of a RuneScape item category_id."""

    id: int
    name: str
    item_count: int

    # @property
    # def db_model(self):
    #     return DBCategory(
    #         id=self.id,
    #         name=self.name,
    #         item_count=self.item_count
    #     )
