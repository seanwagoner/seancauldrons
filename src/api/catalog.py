from fastapi import APIRouter

router = APIRouter()
import sqlalchemy
from src import database as db


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(
                """
                SELECT item_sku, inventory, price, red, green, blue, dark
                FROM potions 
                WHERE inventory > 0
                """
            )).fetchall()

    catalog = []
    for row in result:
        potion_type = [row['red'], row['green'], row['blue'], row['dark']]

        catalog.append({
            "sku": row['item_sku'],
            "name": row['item_sku'].split('_')[0].lower() + " potion",
            "quantity": row['inventory'],
            "price": row['price'],
            "potion_type": potion_type
        })

    return catalog
    

