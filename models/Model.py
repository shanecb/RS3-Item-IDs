from dataclasses import dataclass, astuple
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Any, TypeVar
from peewee import *
import peewee as pw
import models
from utilities import classproperty

ModelType = TypeVar('ModelType', bound='Model')


@dataclass
class Model(ABC):
    """Abstract class that defines the core functionality of a data model."""

    ############################################################################
    # Database Compatibility
    ############################################################################

    # @property
    # def db_model(self):
    #     """
    #     The peewee database model for this Model object.
    #
    #     Use this to access peewee database methods (e.g. insert, update, etc.).
    #     """
    #     # db_class_ = getattr(models, f'DB{self.__class__.__name__}')
    #     # return db_class_(*self.__dict__.values())
    #     db_cls_name = f'DB{self.__class__.__name__}'
    #     db_cls = getattr(models, db_cls_name)
    #
    #     # ForeignKeyAccessor, ObjectIdAccessor, BackrefAccessor
    #     model_dict = self.__dataclass_fields__
    #     model_field_names = model_dict.keys()
    #     db_dict = db_cls.__dict__
    #     db_field_names = [
    #         key for key in db_dict.keys()
    #         if not key.startswith('_')
    #         and (lambda t: t is not pw.ObjectIdAccessor and t is not pw.BackrefAccessor)(type(db_dict[key]))
    #     ]
    #
    #     args = []
    #     eval_globals = {db_cls_name: db_cls}
    #     for f in db_field_names:
    #         if type(db_dict[f]) == pw.ForeignKeyAccessor:
    #             foreign_cls_name = f'DB{"".join([s.capitalize() for s in f.split("_")])}'
    #             model_field = [field for field in model_field_names if field.startswith(f)][0]
    #             id = model_dict[model_field]
    #             args.append(f'{f}={foreign_cls_name}.get({foreign_cls_name}.id == self.{model_field})')
    #             eval_globals[foreign_cls_name] = getattr(models, foreign_cls_name)
    #         elif f not in model_field_names: continue
    #         else:
    #             args.append(f'{f}=self.{f}')
    #
    #     arg_str = ', '.join(args)
    #     expr = f'{db_cls_name}({arg_str})'
    #     print(expr)
    #     return eval(expr, eval_globals, locals())



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

    # @classmethod
    # def select(cls, *fields):
    #     cls.db().select(fields)
    #
    # @classmethod
    # def bulk_create(cls, model_objects, batch_size=None):
    #     cls.db().bulk_create(model_objects, batch_size)
