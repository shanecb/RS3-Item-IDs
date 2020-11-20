from dataclasses import dataclass, field
from typing import Tuple, Dict
from models import Model


@dataclass
class Item(Model):
    """Model of a RuneScape item."""

    id: int = field(default=-1)
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

    @classmethod
    def db_fields_to_keys(cls) -> Dict[str, str]:
        """Overrides the default Model.db_keys() implementation to change the members_only field name."""
        keys = super().db_fields_to_keys()
        keys['members_only'] = 'members'
        return keys

    def db_column_values(self) -> Tuple[int, str, str, str, int]:
        """
        Returns the fields of this Item object as a tuple, converting the members_only field to an int.
        @return: A Tuple of this Item object's fields.
        """
        return self.id, self.name, self.description, self.type, int(self.members_only)



