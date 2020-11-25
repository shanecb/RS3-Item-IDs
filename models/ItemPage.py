from dataclasses import dataclass
from datetime import datetime

from models import Model, DBItemPage, DBCategory


@dataclass
class ItemPage(Model):
    """Model of a request for a page of items with a given category_id id and alpha. Used to track last update times and
    failed requests."""

    category_id: int
    alpha: str
    page_num: int
    last_updated: datetime
    succeeded: bool = False

    @classmethod
    def fetch_by(cls, category_id: int, alpha: str, page_num: int):
        return cls.db.fetch_by(category_id, alpha, page_num)
