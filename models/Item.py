from dataclasses import dataclass, field
from models import Model


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
