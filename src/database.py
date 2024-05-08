import os
import dotenv
from sqlalchemy import create_engine, MetaData
import sqlalchemy

def database_connection_url():
    dotenv.load_dotenv("../../.env")

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)

metadata_obj = sqlalchemy.MetaData()
metadata = MetaData()
metadata.reflect(bind=engine)
carts = metadata.tables['carts']
cart_items = metadata.tables['cart_items']
customers = metadata.tables['customers']
potions = metadata.tables['potions']