from typing import List
from models import *
from api_manager import *
from utilities import log_manager

log = log_manager.get_logger('RS3ItemIds.main')


def save_items_block(items: List[Item]):
    items = [i.db_model.to_dict() for i in items]
    for i in items:
        i['category_id'] = i.pop('category')['id']
        i['item_page_id'] = i.pop('item_page')['id']
    with db.atomic() as txn:
        Item.db.replace_many(items).execute()
        txn.commit()


def save_item_page_block(item_page: ItemPage, item_count: int) -> int:
    with db.atomic() as txn:
        instance = ItemPage.fetch_by(
            item_page.category_id,
            item_page.alpha,
            item_page.page_num
        )
        if instance is None:
            return item_page.create_instance()
        else:
            fields = instance.to_dict()
            category = Category.db.get_or_none(Category.db.id == item_page.category_id)
            if not category:
                log.error(f'Failed to fetch Category associated with ItemPage. (category_id={item_page.category_id}, '
                          f'alpha={item_page.alpha}, page_num={item_page.page_num})')
                return -1
            fields['category'] = category
            fields['alpha'] = item_page.alpha
            fields['page_num'] = item_page.page_num
            fields['last_updated'] = item_page.last_updated
            fields['succeeded'] = item_page.succeeded
            if not item_page.succeeded and item_count < len(instance.items):
                log.error(f'Received less items for page (category_id={item_page.category_id}, '
                          f'alpha={item_page.alpha}, page_num={item_page.page_num}) than what was already stored. '
                          f'Not saving.')
                return -1
            else:
                log.info(f'Replacing entry for ItemPage (category_id={item_page.category_id}, '
                         f'alpha={item_page.alpha}, page_num={item_page.page_num})')
                ItemPage.db.replace(fields).execute()
        txn.commit()
    return instance.id


def update_category_block(category: Category):
    with db.atomic() as txn:
        category.db_model.save()
        txn.commit()


def main():
    for db_category in list(Category.db.select()):
        category = Category(db_category.id, db_category.name, db_category.item_count)
        get_items_in_category(category, save_items_block, save_item_page_block, update_category_block)


main()
