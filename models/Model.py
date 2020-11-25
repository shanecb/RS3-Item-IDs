from dataclasses import dataclass
from abc import ABC
import models
from utilities import classproperty


@dataclass
class Model(ABC):
    """Abstract class that defines the core functionality of a data model."""

    ############################################################################
    # Database Compatibility
    ############################################################################

    @classproperty
    def db(cls) -> models:
        """
        The database table for this Model type.

        Use this to access peewee database methods (e.g. insert, update, etc.).
        """
        return getattr(models, f'DB{cls.__name__}')

    @classmethod
    def fetch(cls, id):
        """
        Fetches the instance of this Model with the given ID in the database.

        @param id: The ID of the Model instance to search for.

        @return: The matching Model if present in the database or None.
        """
        db_instance = cls.db.get_or_none(cls.db.id == id)
        if db_instance is None: return None

        class_ = getattr(models, cls.__name__)
        return class_(*db_instance.__dict__.values())
