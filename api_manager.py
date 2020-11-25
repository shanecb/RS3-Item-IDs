import requests
from typing import List, Dict, Any, Callable
from collections import namedtuple
from models import Item, ItemPage, Category
from utilities import log_manager
import math
import time
from datetime import datetime

__all__ = [
    'get_items_in_category',
    'ItemRequestParams'
]

MAX_RETRIES = 8
RETRY_WAIT_TIME = 11.1
LONG_WAIT_TIME = 300
ITEMS_PER_PAGE = 12

log = log_manager.get_logger('RS3ItemIds.api_manager')
"""Logger object specific to the APIManager."""

ItemRequestParams = namedtuple('ItemRequestParams', ['category_id', 'alpha', 'page_num'])


def _get_with_retry(url: str, params: Dict = None, try_count: int = 0) -> Any:
    if params is None: params = {}

    def recurse() -> Any:
        time.sleep(RETRY_WAIT_TIME)
        if try_count >= 5:
            log.warning('Retries have not succeeded... waiting long time now.')
            time.sleep(LONG_WAIT_TIME)
        log.info(f'Retrying GET request to url: {url}, with params: {params} (attempt {try_count + 1}).')
        return _get_with_retry(url, params, try_count + 1)

    if try_count >= MAX_RETRIES:
        log.error(f'Failed to execute GET request to url: {url} after {MAX_RETRIES} tries.')
        return None

    r = requests.get(url, params=params)
    log.debug(f'Received response: {r.content}')

    if r.status_code not in range(200, 299):
        log.info(f'GET request to url: {url} failed with status code {r.status_code}.')
        return recurse()

    if len(r.text) == 0:
        log.info(f'Result of GET was empty. May have hit rate limit.')
        return recurse()

    try:
        return r.json()
    except ValueError as e:
        log.warning(f'Failed to get JSON content from {r.content}. ValueError: {e}')
        return recurse()


def get_alpha_counts(category_id: int) -> Dict[str, int]:
    """
    Makes a GET request to the catalogue/category_id endpoint and returns a dictionary of all alphas and their counts
    where the count is not 0.

    @param category_id: The category_id identifier.

    @return: A dictionary of alphas and their respective counts.
    """
    log.info(f'Attempting to get alpha counts for category: {category_id}.')

    json = _get_with_retry(
        'https://services.runescape.com/m=itemdb_rs/api/catalogue/category.json',
        params={'category': category_id}
    )

    return {a['letter']: a['items'] for a in json['alpha'] if a['items'] != 0}


def get_items_with_letter_in_category_on_page(params: ItemRequestParams) -> List[Item]:
    """
    Makes a GET request to the catalogue/items.json endpoint and returns the items on the given page number.

    @param params: ItemRequestParams with the category_id id, first letter, and page number to get.

    @return: A list of Item objects.
    """
    json = _get_with_retry(
        'https://services.runescape.com/m=itemdb_rs/api/catalogue/items.json',
        params={'category': params.category_id, 'alpha': params.alpha, 'page': params.page_num}
    )

    return [
        Item(id=i['id'], name=i['name'], description=i['description'], type=i['type'], members_only=i['members'])
        for i in json['items']
    ]


def get_items_in_category(
        category: Category,
        save_items_block: Callable[[List[Item]], None],
        save_item_page_block: Callable[[ItemPage, int], int],
        update_category_block: Callable[[Category], None]
) -> List[ItemRequestParams]:
    """
    Gets all items in the given category, saving to database after completing each alpha set (group of items that
    start with a certain letter).

    @param category: The category to get the items for. @param save_alpha_block: A completion block that will be
    called with all items with a given first letter after they've been successfully fetched.
    @param save_items_block: The function to call to save each list of items which start with a given letter.
    @param save_item_page_block: The function to call to save each item page.
    @param update_category_block: The function to call to update the category.

    @return: List of Tuples with the category, letter, and page number of failed requests.
    """
    alphas = get_alpha_counts(category.id)
    if '#' in alphas: alphas['%23'] = alphas.pop('#')
    expected_total_count = sum(alphas.values())

    # dict of letters to the number of page requests needed to get all items starting with that letter
    request_alphas = {letter: math.ceil(count / ITEMS_PER_PAGE) for letter, count in alphas.items()}

    log.info(f'Alphas to page counts: {request_alphas}.')
    log.info(f'Attempting to get {expected_total_count} items from category_id: {category.id}.')

    total_count = 0
    for letter, count in request_alphas.items():
        last_page_count = alphas[letter] % ITEMS_PER_PAGE
        # fix the edge case where number of items on last page is equal to the max items per page (modulo result is 0)
        if not last_page_count: last_page_count = ITEMS_PER_PAGE
        items: List[Item] = []
        for page_num in range(1, count + 1):
            expected_count = (last_page_count, ITEMS_PER_PAGE)[page_num < count]
            params = ItemRequestParams(category.id, letter, page_num)
            page: List[Item] = get_items_with_letter_in_category_on_page(params)

            item_page = ItemPage(
                category_id=category.id,
                alpha=letter,
                page_num=page_num,
                last_updated=datetime.utcnow()
            )

            actual_count = len(page)
            if actual_count != expected_count:
                log.warning(f'Incorrect number of items found on page: {page_num}. Expected: {expected_count}, but got:'
                            f' {actual_count} (category_id={category.id}, alpha={letter}, page={page_num})')
                item_page.succeeded = False
            else:
                item_page.succeeded = True
            db_item_page_id = save_item_page_block(item_page, actual_count)
            if db_item_page_id is None:
                log.error('Failed to create item page in db.')

            page = [
                Item(
                    id=i.id,
                    category_id=category.id,
                    item_page_id=db_item_page_id,
                    name=i.name,
                    description=i.description,
                    type=i.type,
                    members_only=i.members_only
                )
                for i in page
            ]
            items += page

        save_items_block(items)
        total_count += len(items)

    if total_count != expected_total_count:
        log.warning(f'Count of items retrieved from category_id: {category.id} not equal to expected total: '
                    f'{expected_total_count}. Only got {total_count} items.')

    category.item_count = total_count
    update_category_block(category)
