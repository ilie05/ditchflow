import os
from flask_sqlalchemy import SQLAlchemy
import sqlite3

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# used for manager.py script
# connect/create new database

current_folder = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(current_folder, 'db.sqlite')

conn = sqlite3.connect(db_file)
# create Cursor to execute queries
cursor = conn.cursor()
