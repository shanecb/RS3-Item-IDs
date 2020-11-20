import requests
from typing import List, Dict, Any
from models import Item
from utilities import log_manager
import time
# from rs3_api_constants import *
import rs3_api_constants as api
import pprint

MAX_RETRIES = 5
RETRY_WAIT_TIME = 5.1

log = log_manager.get_logger('RS3ItemIds.api_manager')
"""Logger object specific to the APIManager."""


def _get_with_retry(url: str, params: Dict = {}, try_count: int = 0) -> Any:
    def recurse() -> Any:
        time.sleep(RETRY_WAIT_TIME)
        log.info(f'Retrying GET request to url: {url} (attempt {try_count + 1}).')
        return _get_with_retry(url, try_count + 1)

    if try_count >= MAX_RETRIES:
        log.error(f'Failed to execute GET request to url: {url} after {MAX_RETRIES} tries.')
        return None

    r = requests.get(url, params=params)
    log.info(f'Received response: {r.content}')

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
    Makes a GET request to the catalogue/category endpoint and returns a dictionary of all alphas and their counts where the count is not 0.

    @param category: The category identifier.

    @return: A dictionary of alphas and their respective counts.
    """
    log.info('Attempting to get alpha counts.')

    json = _get_with_retry(
        'https://services.runescape.com/m=itemdb_rs/api/catalogue/category.json',
        params={'category': category}
    )

    return {a['letter']: a['items'] for a in json['alpha'] if a['items'] != 0}


def get_items_with_letter_in_category_on_page(
        letter: str,
        category: int,
        page: int
) -> List[Item]:
    """
    Makes a GET request to the catalogue/items.json endpoint and returns the items on the given page number.

    @param letter: The first letter of the items you wish to find.
    @param category: The category identifier.
    @param page: The page number to return.

    @return: A list of Item objects.
    """
    json = _get_with_retry(
        'https://services.runescape.com/m=itemdb_rs/api/catalogue/items.json',
        params={'category': category, 'alpha': letter, 'page': page}
    )

    return [
        Item(i['id'], i['name'], i['description'], i['type'], i['members'])
        for i in json['items']
    ]


# def get_items_in_category(category: int) -> List[Item]:



for c in api.categories:
    print(f'{api.categories[c]}\n')
    alphas = get_alpha_counts(c)
    total = sum(alphas.values())
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(alphas)
    print(f'\ntotal: {total}')
