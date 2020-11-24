from dataclasses import dataclass, astuple
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Any
import sys
import models
from utilities import classproperty


@dataclass
class Model(ABC):
    """Abstract class that defines the core functionality of a data model."""

    ############################################################################
    # Database Compatibility
    ############################################################################

    @property
    def db_model(self):
        """
        The peewee database model for this Model object.

        Use this to access peewee database methods (e.g. insert, update, etc.).
        """
        class_ = getattr(models, f'DB{self.__class__.__name__}')
        return class_(*self.__dict__.values())

    @classproperty
    def db(cls) -> models:
        """
        The database table for this Model type.

        Use this to access peewee database methods (e.g. insert, update, etc.).
        """
        return getattr(models, f'DB{cls.__name__}')

    # @classmethod
    # def select(cls, *fields):
    #     cls.db().select(fields)
    #
    # @classmethod
    # def bulk_create(cls, model_objects, batch_size=None):
    #     cls.db().bulk_create(model_objects, batch_size)
