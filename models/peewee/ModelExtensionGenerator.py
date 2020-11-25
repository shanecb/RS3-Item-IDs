#!/usr/bin/env python
import ast
from typing import Any, Union, Dict, List, Tuple
from dataclasses import dataclass

"""Code generator to add utility functions to Model classes for interfacing with peewee models."""


@dataclass
class DBField:
    name: str
    type: str
    args: List[str]
    keywords: Dict[str, str]


class FieldParser(ast.NodeVisitor):
    def visit_Assign(self, node: ast.Assign) -> DBField:
        name = [n.id for n in node.targets if isinstance(n, ast.Name)][0]
        type_ = node.value.func.id
        args = [n.id for n in node.value.args]
        keywords = {n.arg: n.value.value for n in node.value.keywords}
        return DBField(name, type_, args, keywords)


def _tab(size):
    return ' ' * size


class ModelExtension:

    def __init__(self, model: str, db_model: str, fields: List[DBField]):
        self.model = model
        self.db_model = db_model
        self.fields = fields

    def gen_ext_strs(self) -> Tuple[str, str]:
        """
        Generates the code for this extension and the .pyi type hint stub code.

        @return: A Tuple with the extension code and the corresponding type hint stub code.
        """
        comment_line = '#' * 80
        base_str = (
            f'{comment_line}\n'
            f'# {self.model}\n'
            f'{comment_line}\n'
        )

        stub_base_str = (
            f'{base_str}\n'
            f'class {self.model}:'
        )

        code, type_stub = zip(*[
            (base_str, stub_base_str),
            self.gen_db_model_fn(),
            self.gen_create_instance_fn()
        ])

        return '\n\n'.join(list(code)), '\n\n'.join(list(type_stub))

    def _gen_args_str(self, indent_size: int = 8):
        arg_strings: List[str] = []
        for f in self.fields:
            self_name = f'self.{f.name}'
            if f.type == 'AutoField':
                continue
            elif f.type == 'ForeignKeyField':
                foreign_model_name = f'DB{"".join([s.capitalize() for s in f.name.split("_")])}'
                arg_strings.append(f'{f.name}={foreign_model_name}.get({foreign_model_name}.id == {self_name}_id)')
            else:
                arg_strings.append(f'{f.name}={self_name}')

        return f',\n{_tab(indent_size)}'.join(arg_strings)

    def _gen_fn_str(self, fn_name1: str, fn_name2: str, def_str: str) -> str:
        """
        Generates the string that defines a function and dynamically assigns it to a class.
        @param fn_name1: The name of the function as defined locally in the extension file.
        @param fn_name2: The name of the function as it will be accessed on the class.
        @param def_str: The definition of the function that will be added to the class.
        @return: The full string - ready to be appended to the extension file.
        """
        return (
            f'{def_str}\n\n'
            f'{self.model}.{fn_name2} = {fn_name1}\n'
        )

    @staticmethod
    def _gen_fn_type_stub(name_and_args: str, type_: str, comment: str):
        return f'{_tab(4)}def {name_and_args} -> {type_}: ...\n{comment}'

    @staticmethod
    def _gen_property_type_stub(name: str, type_: str, comment: str):
        return f'{_tab(4)}{name}: {type_}\n{comment}'

    @staticmethod
    def _gen_doc_comment_str(comment: str, indent_size: int = 4):
        tab = _tab(indent_size)
        return f'\n{tab}'.join([f'{tab}"""'] + comment.split('\n') + ['"""'])

    def gen_db_model_fn(self) -> Tuple[str, str]:
        fn_name1 = f'_{self.model.lower()}_db_model'
        fn_name2 = 'db_model'
        comment_str = self._gen_doc_comment_str(
            'The peewee database model for this Model object.\n\n'
            'Use this to access peewee database methods (e.g. insert, update, etc.).'
        )
        def_string = (
            f'@property\n'
            f'def {fn_name1}(self) -> {self.db_model}:\n'
            f'{comment_str}\n'
            f'    return {self.db_model}(\n'
            f'        {self._gen_args_str()}\n'
            f'    )\n'
        )
        return (
            self._gen_fn_str(fn_name1, fn_name2, def_string),
            self._gen_property_type_stub(fn_name2, self.db_model, comment_str)
        )

    def gen_create_instance_fn(self) -> Tuple[str, str]:
        fn_name1 = f'_{self.model.lower()}_create_instance'
        fn_name2 = 'create_instance'
        comment_str = self._gen_doc_comment_str(
            'Inserts this model object as a new row into table and returns corresponding model instance.\n\n'
            'Useful for populating an AutoField primary key.'
        )
        def_string = (
            f'def {fn_name1}(self):\n'
            f'{comment_str}\n'
            f'    return {self.model}.db.create(\n'
            f'        {self._gen_args_str()}\n'
            f'    )\n'
        )
        return (
            self._gen_fn_str(fn_name1, fn_name2, def_string),
            self._gen_fn_type_stub(f'{fn_name2}(self)', self.db_model, comment_str)
        )


def main():
    tree: Union[ast.Module, ast.AST]
    with open('peewee_models.py', 'r') as f:
        tree = ast.parse(f.read())

    # print(ast.dump(tree, indent=4))

    classes = [
        c for c in tree.body
        if isinstance(c, ast.ClassDef)
        and 'DBBaseModel' in [n.id for n in c.bases]
    ]

    base_str = 'from models import *\n\n# AUTOGENERATED FILE. DO NOT MODIFY!\n\n'
    extension_file_str = f'{base_str}__all__ = []\n\n\n'
    type_stub_file_str = f'{base_str}\n'

    for c in classes:
        # print(ast.dump(c, indent=4))
        # print(c.name)
        # print('-' * len(c.name))
        fields = [FieldParser().visit(n) for n in c.body if isinstance(n, ast.Assign)]
        # for f in fields:
        #     print(f' - {f.name}')
        #     print(f'    * type: {f.type:11}')
        #     if f.args:
        #         print(f'    * args:     {f.args}')
        #     if f.keywords:
        #         print(f'    * keywords: {f.keywords}')
        # print()

        model_name = c.name[2:]

        code, type_stub = ModelExtension(model_name, c.name, fields).gen_ext_strs()
        extension_file_str += f'{code}\n\n'
        type_stub_file_str += f'{type_stub}\n\n'

    with open('ModelExtensions.py', 'w+') as f:
        f.write(extension_file_str)

    with open('ModelExtensions.pyi', 'w+') as f:
        f.write(type_stub_file_str)


if __name__ == "__main__":
    main()

"""
DBCategory
----------
 - id
    * type: IntegerField
    * keywords: {'primary_key': True}
 - name
    * type: CharField  
 - item_count
    * type: IntegerField
    * keywords: {'default': 0}

DBItemPage
----------
 - id
    * type: AutoField  
 - category
    * type: ForeignKeyField
    * args:     ['DBCategory']
    * keywords: {'backref': 'page_requests'}
 - alpha
    * type: CharField  
 - page_num
    * type: IntegerField
 - last_updated
    * type: DateTimeField
 - succeeded
    * type: BooleanField
    * keywords: {'default': False}

DBItem
------
 - id
    * type: IntegerField
    * keywords: {'primary_key': True}
 - category
    * type: ForeignKeyField
    * args:     ['DBCategory']
    * keywords: {'backref': 'items'}
 - item_page
    * type: ForeignKeyField
    * args:     ['DBItemPage']
    * keywords: {'backref': 'items'}
 - name
    * type: CharField  
 - description
    * type: CharField  
 - type
    * type: CharField  
 - members_only
    * type: BooleanField
"""

# from dataclasses import dataclass, astuple
# from abc import ABC, abstractmethod
# from typing import Tuple, Dict, List, Any
# import sys
#
#
# @dataclass
# class Model(ABC):
#     """Abstract class that defines the core functionality of a data model."""
#
#     ############################################################################
#     # Database Compatibility
#     ############################################################################
#
#     @classmethod
#     def db_table_name(cls) -> str:
#         return cls.__name__.lower() + 's'
#
#     @classmethod
#     def db_fields_to_keys(cls) -> Dict[str, str]:
#         """
#         Dict of dataclass field names and their associated database keys.
#
#         @note If a subclass has an id field, this method automagically prepends the class name to '_id' for that db key.
#         """
#         keys = {field: field for field in cls.__dataclass_fields__.keys()}
#         if 'id' in keys.keys():
#             keys['id'] = cls.__name__.lower() + '_id'
#
#     @classmethod
#     def db_keys_to_fields(cls) -> Dict[str, str]:
#         """
#         Dict of database keys and their associated field names in the model object.
#         """
#         return {val: key for key, val in cls.db_fields_to_keys().items()}
#
#     @classmethod
#     def db_primary_keys(cls) -> List[str]:
#         """
#         Returns the names of the primary keys for this Model type's database table.
#
#         @note This must be overwritten if the subclass does not have an id field or if id is not used as the primary key.
#         """
#         if 'id' not in cls.__dataclass_fields__.keys():
#             sys.exit(f'{cls.__name__} does not have \'id\' field. Overwrite the db_primary_keys() method or add \'id\' '
#                      f'field.')
#         return [cls.db_fields_to_keys()['id']]
#
#     def db_primary_keys_and_values(self) -> Dict[str, Any]:
#         """
#         Returns a Dict of key names and their associated values to use as primary keys.
#
#         @note This must be overwritten if the subclass does not have an id field or if id is not used as the primary key.
#         """
#         if 'id' not in self.__dataclass_fields__.keys() or 'id' not in self.db_primary_keys():
#             sys.exit(f'{self.__name__} does not have \'id\' field or does not use id as a primary key. Overwrite the db_primary_keys_and_values() method or add \'id\' '
#                      f'field.')
#         return {key: getattr(self, self.db_keys_to_fields()[key]) for key in self.db_primary_keys()}
#
#     @classmethod
#     def db_column_name_str(cls) -> str:
#         """Returns a str listing the db_keys formatted correctly to be used in a SQL command."""
#         return '(' + ', '.join(cls.db_fields_to_keys().values()) + ')'
#
#     @classmethod
#     def db_column_template_str(cls) -> str:
#         """Returns a str of question marks separated by commas to use in SQL commands."""
#         return f'({", ".join(["?" for _ in cls.db_fields_to_keys()])})'
#
#     def db_column_values(self) -> Tuple:
#         """
#         Returns the fields of this Model object as a tuple.
#         @return: A Tuple of this Model object's field values.
#         """
#         """Returns this object's field values as a Tuple."""
#         return astuple(self)
