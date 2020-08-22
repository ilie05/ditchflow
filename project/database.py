from flask_sqlalchemy import SQLAlchemy
import sqlite3

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# used for manager.py script
# connect/create new database
conn = sqlite3.connect('db.sqlite')
# create Cursor to execute queries
cursor = conn.cursor()
