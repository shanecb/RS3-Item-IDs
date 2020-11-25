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

    # @property
    # def db_model(self):
    #     return DBItemPage(
    #         category=DBCategory.get(DBCategory.id == self.category_id),
    #         alpha=self.alpha,
    #         page_num=self.page_num,
    #         last_update=self.last_updated,
    #         succeeded=self.succeeded
    #     )
