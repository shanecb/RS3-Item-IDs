# script to create a sqlite3 database of rs3 item ids

import argparse
import sqlite3

parser = argparse.ArgumentParser(description="Automatically create an empty rs3 item database.")
parser.add_argument(
    '-n',
    metavar="database name",
    type=str,
    required=False,
    default='rs3-items.db',
    help='sqlite3 database filename'
)
args = parser.parse_args()

# create table commands
CREATE_ITEMS = 'CREATE TABLE items (item_id INTEGER PRIMARY KEY, full_name TEXT, description TEXT, type TEXT, ' \
               'members_only INTEGER, category_id INTEGER FOREIGN KEY); '
CREATE_CATEGORIES = 'CREATE TABLE categories (category_id INTEGER PRIMARY KEY, name TEXT, count INTEGER);'

commands = [CREATE_ITEMS, CREATE_CATEGORIES]
# create database
conn = sqlite3.connect(args.n)
c = conn.cursor()

for command in commands:
    c.execute(command)
conn.commit()
conn.close()
