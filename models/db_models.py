from peewee import *

__all__ = [
    'DBCategory',
    'DBItem',
    'db'
]

db = SqliteDatabase('rs3-items.db')


def _make_table_name(model_class: Model):
    return model_class.__name__[2:]


class DBBaseModel(Model):
    """Sets database on Meta class so that models that subclass this base model don't have to."""

    class Meta:
        database = db
        # legacy_table_names = False
        table_function = _make_table_name


class DBCategory(DBBaseModel):
    """Model of a RuneScape item category."""
    id = IntegerField(primary_key=True)
    name = CharField()
    item_count = IntegerField(default=0)
    last_update = DateTimeField(null=True)


class DBItem(DBBaseModel):
    """Model of a RuneScape item."""
    id = IntegerField(primary_key=True)
    category = ForeignKeyField(DBCategory, backref='items')
    name = CharField()
    description = CharField()
    type = CharField()
    members_only = BooleanField()



