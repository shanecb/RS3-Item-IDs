import json
import requests
from typing import List
from models import *
from db_manager import *
from api_manager import *

# get all categories in the database
categories = list(Category.db.select())


def save_alpha_block(items: List[Item]):
    with db.atomic() as txn:
        Item.db.bulk_create(items)
        txn.commit()


failed_requests = get_items_in_category(0, save_alpha_block)

print('\n\nThe following requests failed:')
print('------------------------------')
for failed_request in failed_requests:
    print(failed_request)
