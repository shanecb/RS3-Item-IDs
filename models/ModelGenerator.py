from dataclasses import dataclass, astuple
from abc import ABC, abstractmethod
from typing import Tuple, Dict, List, Any
import sys


@dataclass
class Model(ABC):
    """Abstract class that defines the core functionality of a data model."""

    ############################################################################
    # Database Compatibility
    ############################################################################

    @classmethod
    def db_table_name(cls) -> str:
        return cls.__name__.lower() + 's'

    @classmethod
    def db_fields_to_keys(cls) -> Dict[str, str]:
        """
        Dict of dataclass field names and their associated database keys.

        @note If a subclass has an id field, this method automagically prepends the class name to '_id' for that db key.
        """
        keys = {field: field for field in cls.__dataclass_fields__.keys()}
        if 'id' in keys.keys():
            keys['id'] = cls.__name__.lower() + '_id'

    @classmethod
    def db_keys_to_fields(cls) -> Dict[str, str]:
        """
        Dict of database keys and their associated field names in the model object.
        """
        return {val: key for key, val in cls.db_fields_to_keys().items()}

    @classmethod
    def db_primary_keys(cls) -> List[str]:
        """
        Returns the names of the primary keys for this Model type's database table.

        @note This must be overwritten if the subclass does not have an id field or if id is not used as the primary key.
        """
        if 'id' not in cls.__dataclass_fields__.keys():
            sys.exit(f'{cls.__name__} does not have \'id\' field. Overwrite the db_primary_keys() method or add \'id\' '
                     f'field.')
        return [cls.db_fields_to_keys()['id']]

    def db_primary_keys_and_values(self) -> Dict[str, Any]:
        """
        Returns a Dict of key names and their associated values to use as primary keys.

        @note This must be overwritten if the subclass does not have an id field or if id is not used as the primary key.
        """
        if 'id' not in self.__dataclass_fields__.keys() or 'id' not in self.db_primary_keys():
            sys.exit(f'{self.__name__} does not have \'id\' field or does not use id as a primary key. Overwrite the db_primary_keys_and_values() method or add \'id\' '
                     f'field.')
        return {key: getattr(self, self.db_keys_to_fields()[key]) for key in self.db_primary_keys()}

    @classmethod
    def db_column_name_str(cls) -> str:
        """Returns a str listing the db_keys formatted correctly to be used in a SQL command."""
        return '(' + ', '.join(cls.db_fields_to_keys().values()) + ')'

    @classmethod
    def db_column_template_str(cls) -> str:
        """Returns a str of question marks separated by commas to use in SQL commands."""
        return f'({", ".join(["?" for _ in cls.db_fields_to_keys()])})'

    def db_column_values(self) -> Tuple:
        """
        Returns the fields of this Model object as a tuple.
        @return: A Tuple of this Model object's field values.
        """
        """Returns this object's field values as a Tuple."""
        return astuple(self)
