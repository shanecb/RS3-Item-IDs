from dataclasses import dataclass, field
from typing import Tuple, Dict
from models import Model, DBItem, DBItemPage, DBCategory


@dataclass
class Item(Model):
    """Model of a RuneScape item."""

    id: int = field(default=-1)
    category_id: int = field(default=None)
    item_page_id: int = field(default=None)
    name: str = field(default='')
    description: str = field(default='')
    type: str = field(default='')
    members_only: bool = field(default=True)

    def __post_init__(self):
        """Ensure types of fields are correct"""
        # Ensures that members_only field is a bool
        if type(self.members_only) is str:
            self.members_only = (False, True)[str(self.members_only).lower() == 'true']
        elif type(self.members_only) is int:
            self.members_only = bool(self.members_only)

    # @property
    # def db_model(self):
    #     return DBItem(
    #         id=self.id,
    #         # DBCategory.get(DBCategory.id == self.category_id),
    #         # DBItemPage.get(DBItemPage.id == self.item_page_id),
    #         category_id=self.category_id,
    #         item_page_id=self.item_page_id,
    #         name=self.name,
    #         description=self.description,
    #         type=self.type,
    #         members_only=self.members_only
    #     )



