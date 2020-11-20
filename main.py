import json
import requests
from models import Item
from db_manager import DBManager


db_manager = DBManager()

items = [Item(i+1000, str(i), str(i), str(i), True) for i in range(16)]
[db_manager.insert_item(i) for i in items]

i5 = db_manager.fetch_items('5')

print(i5)


