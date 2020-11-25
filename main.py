import json
import requests
from typing import List
from models import *
from db_manager import *
from api_manager import *

# get all categories in the database
categories = list(Category.db.select())


def save_alpha_block(items: List[Item]):
    items = [i.db_model for i in items]
    with db.atomic() as txn:
        Item.db.bulk_create(items)
        txn.commit()


def save_item_page_block(item_page: ItemPage) -> int:
    with db.atomic() as txn:
        # db_item_page = ItemPage.db.create(
        #     category=item_page.category_id,
        #     alpha=item_page.alpha,
        #     page_num=item_page.page_num,
        #     last_updated=item_page.last_updated,
        #     succeeded=item_page.succeeded
        # )
        db_item_page = item_page.create_instance()
        txn.commit()
    return db_item_page.id


def update_category_block(category: Category):
    with db.atomic() as txn:
        category.db_model.save()
        txn.commit()


def main():
    category = Category(categories[0].id, categories[0].name, 0)
    failed_requests = get_items_in_category(category, save_alpha_block, save_item_page_block, update_category_block)

    print('\n\nThe following requests failed:')
    print('------------------------------')
    for failed_request in failed_requests:
        print(failed_request)


main()
