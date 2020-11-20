import sqlite3
from typing import List, Any
from models import Model, Item, Category
from utilities import log_manager


log = log_manager.get_logger('RS3ItemIds.api_manager')
"""Logger object specific to the APIManager."""

class DBManager:

    def __init__(self, db_name='rs3-items.db', debugging=False):
        self.db_connection = sqlite3.connect(db_name)

        self.debugging = debugging #if debugging is true, db_manager will write information to the terminal

    ########################
    # fetch methods (SELECT)
    ########################

    def fetch_items(self, name: str) -> List[Item]:
        """
        Fetches an item by it's name.

        @param name: The name of the item to fetch.

        @return: The items in the database whose names match the given name.
        """
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT * FROM items WHERE full_name=?', name)
        items: list[Any] = cursor.fetchall()
        cursor.close()

        return [Item(*i) for i in items]

    #########################
    # insert methods (INSERT)
    #########################

    def insert(self, model: Model):
        """Inserts a Model object into the table with the given name."""
        cmd = f'INSERT INTO {model.db_table_name()} {model.db_column_name_str()} VALUES {model.db_column_template_str()}'
        params = model.db_column_values()

        cursor = self.db_connection.cursor()
        try:
            cursor.execute(cmd, params)
        except sqlite3.IntegrityError as e:
            log.warning(f'Entry already exists in table: {model.db_table_name()}')
        else:
            self.db_connection.commit()

    ##############################
    # change current info (UPDATE)
    ##############################

    def update(self, model: Model):
        """
        Updates a Model object in the database.
        @param model: The Model object to update.
        """
        keys_to_set = [key for key in model.db_keys_to_fields().keys() if key not in model.db_primary_keys()]
        set_template = ', '.join([key + '=?' for key in keys_to_set])
        condition_template = ', '.join([key + '=?' for key in model.db_primary_keys()])
        cmd = f'UPDATE {model.db_table_name()} SET {set_template} WHERE {condition_template}'
        params = [getattr(model, model.db_keys_to_fields()[key]) for key in keys_to_set + model.db_primary_keys()]

        cursor = self.db_connection.cursor()
        cursor.execute(
            cmd,
            params
        )
        self.db_connection.commit()
        cursor.close()

    def update_item(self, item: Item):
        """
        Updates the item with the given ID in the database.
        @param item: The new Item object that will be inserted in place of the old one.
        """
        cursor = self.db_connection.cursor()
        cursor.execute(
            'UPDATE items SET full_name=?, description=?, type=?, members_only=? WHERE item_id=?',
            (item.name, item.description, item.type, int(item.members_only), item.id)
        )
        self.db_connection.commit()
        cursor.close()