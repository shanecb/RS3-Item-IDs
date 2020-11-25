from models import db, DBCategory, DBItemPage, DBItem
from rs3_api_constants import item_categories
from utilities import log_manager

log = log_manager.get_logger('RS3ItemIds.api_manager')
"""Logger object specific to the APIManager."""

MODELS = [DBCategory, DBItemPage, DBItem]

__all__ = [
    'create_tables',
    'populate_item_categories'
]


def create_tables():
    """Creates database tables for each model if they do not already exist."""
    db.connect()
    db.create_tables(MODELS)
    db.close()


def populate_item_categories():
    """Inserts categories generated from the categories dictionary in rs3_api_constants.py"""
    categories = [DBCategory(id=category_id, name=name) for category_id, name in item_categories.items()]
    DBCategory.bulk_create(categories)


if __name__ == "__main__":
    create_tables()
    populate_item_categories()
