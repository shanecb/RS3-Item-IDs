import peewee as pw
from playhouse.shortcuts import model_to_dict

__all__ = [
    'Model',
    'Category',
    'ItemPage',
    'Item',
    'db'
]

db = pw.SqliteDatabase('rs3-items.db')


class Model(pw.Model):
    """Sets database on Meta class so that models that subclass this base model don't have to."""

    class Meta:
        database = db
        legacy_table_names = False

    def to_dict(self):
        return model_to_dict(self)


class Category(Model):
    """Model of a RuneScape item category_id."""
    id = pw.IntegerField(primary_key=True)
    name = pw.CharField()
    item_count = pw.IntegerField(default=0)


class ItemPage(Model):
    """Model of a request for a page of items with given category_id id and alpha. Used to track last update times and
    failed requests. """
    id = pw.AutoField()
    category = pw.ForeignKeyField(Category, backref='page_requests')
    alpha = pw.CharField()
    page_num = pw.IntegerField()
    last_updated = pw.DateTimeField()
    succeeded = pw.BooleanField(default=False)

    @classmethod
    def fetch_by(cls, category_id: int, alpha: str, page_num: int):
        category = Category.get_or_none(Category.id == category_id)
        return cls.get_or_none(
            cls.category == category,
            cls.alpha == alpha,
            cls.page_num == page_num
        )


class Item(Model):
    """Model of a RuneScape item."""
    id = pw.IntegerField(primary_key=True)
    category = pw.ForeignKeyField(Category, backref='items')
    item_page = pw.ForeignKeyField(ItemPage, backref='items')
    name = pw.CharField()
    description = pw.CharField()
    type = pw.CharField()
    members_only = pw.BooleanField()