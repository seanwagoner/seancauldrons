from fastapi import APIRouter

router = APIRouter()
import sqlalchemy
from src import database as db


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    sql_to_fetch = "SELECT num_green_potions FROM global_inventory"
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_fetch)).fetchone()
    
    num_green_potions = 1 if result[0] else 0

    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": num_green_potions,
                "price": 50,
                "potion_type": [0, 100, 0, 0],
            }
        ]
