from peewee import *
from playhouse.shortcuts import model_to_dict

__all__ = [
    'DBCategory',
    'DBItemPage',
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

    def to_dict(self):
        return model_to_dict(self)


class DBCategory(DBBaseModel):
    """Model of a RuneScape item category_id."""
    id = IntegerField(primary_key=True)
    name = CharField()
    item_count = IntegerField(default=0)


class DBItemPage(DBBaseModel):
    """Model of a request for a page of items with given category_id id and alpha. Used to track last update times and
    failed requests. """
    id = AutoField()
    category = ForeignKeyField(DBCategory, backref='page_requests')
    alpha = CharField()
    page_num = IntegerField()
    last_updated = DateTimeField()
    succeeded = BooleanField(default=False)

    @classmethod
    def fetch_by(cls, category_id: int, alpha: str, page_num: int):
        category = DBCategory.get_or_none(DBCategory.id == category_id)
        return cls.get_or_none(
            cls.category == category,
            cls.alpha == alpha,
            cls.page_num == page_num
        )


class DBItem(DBBaseModel):
    """Model of a RuneScape item."""
    id = IntegerField(primary_key=True)
    category = ForeignKeyField(DBCategory, backref='items')
    item_page = ForeignKeyField(DBItemPage, backref='items')
    name = CharField()
    description = CharField()
    type = CharField()
    members_only = BooleanField()
