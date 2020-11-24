import requests
from typing import List, Dict, Any, Callable
from collections import namedtuple
from models import Item
from utilities import log_manager
import math
import time

__all__ = [
    'get_items_in_category',
    'ItemRequestParams'
]

MAX_RETRIES = 5
RETRY_WAIT_TIME = 5.1
ITEMS_PER_PAGE = 12

log = log_manager.get_logger('RS3ItemIds.api_manager')
"""Logger object specific to the APIManager."""

ItemRequestParams = namedtuple('ItemRequestParams', ['categoryId', 'alpha', 'page_num'])


def _get_with_retry(url: str, params: Dict = None, try_count: int = 0) -> Any:
    if params is None: params = {}

    def recurse() -> Any:
        time.sleep(RETRY_WAIT_TIME)
        log.info(f'Retrying GET request to url: {url} (attempt {try_count + 1}).')
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


def get_alpha_counts(category: int) -> Dict[str, int]:
    """
    Makes a GET request to the catalogue/category endpoint and returns a dictionary of all alphas and their counts
    where the count is not 0.

    @param category: The category identifier.

    @return: A dictionary of alphas and their respective counts.
    """
    log.info('Attempting to get alpha counts.')

    json = _get_with_retry(
        'https://services.runescape.com/m=itemdb_rs/api/catalogue/category.json',
        params={'category': category}
    )

    return {a['letter']: a['items'] for a in json['alpha'] if a['items'] != 0}


def get_items_with_letter_in_category_on_page(params: ItemRequestParams) -> List[Item]:
    """
    Makes a GET request to the catalogue/items.json endpoint and returns the items on the given page number.

    @param params: ItemRequestParams with the category id, first letter, and page number to get.

    @return: A list of Item objects.
    """
    json = _get_with_retry(
        'https://services.runescape.com/m=itemdb_rs/api/catalogue/items.json',
        params={'category': params.categoryId, 'alpha': params.alpha, 'page': params.page_num}
    )

    return [
        Item(i['id'], i['name'], i['description'], i['type'], i['members'])
        for i in json['items']
    ]


def get_items_in_category(category: int, save_alpha_block: Callable[[List[Item]], None]) -> List[ItemRequestParams]:
    """
    Gets all items in the given category, saving to database after completing each alpha set (group of items that
    start with a certain letter).

    @param category: The ID of the category to get the items for. @param save_alpha_block: A completion block that will be
    called with all items with a given first letter after they've been successfully fetched.
    @param save_alpha_block: The function to call to save each list of items which start with a given letter.

    @return: List of Tuples with the category, letter, and page number of failed requests.
    """
    alphas = get_alpha_counts(category)
    if '#' in alphas: alphas['%23'] = alphas.pop('#')
    expected_total_count = sum(alphas.values())

    request_alphas = {letter: math.ceil(count / ITEMS_PER_PAGE) for letter, count in alphas.items()}

    log.info(f'Alphas to page counts: {request_alphas}.')
    log.info(f'Attempting to get {expected_total_count} items from category: {category}.')

    failed_requests = []
    total_count = 0
    for letter, count in request_alphas.items():
        last_page_count = alphas[letter] % ITEMS_PER_PAGE
        items: List[Item] = []
        for page_num in range(1, count + 1):
            expected_count = (last_page_count, ITEMS_PER_PAGE)[page_num < count]
            params = ItemRequestParams(category, letter, page_num)
            page: List[Item] = get_items_with_letter_in_category_on_page(params)
            actual_count = len(page)
            if actual_count != expected_count:
                log.warning(f'Incorrect number of items found on page: {page_num}. Expected: {expected_count}, but got:'
                            f' {actual_count} (category={category}, alpha={letter}, page={page_num}')
                failed_requests += params
            items += page

        save_alpha_block(items)
        total_count += len(items)

    if total_count != expected_total_count:
        log.warning(f'Count of items retrieved from category: {category} not equal to expected total: '
                    f'{expected_total_count}. Only got {total_count} items.')

    return failed_requests
