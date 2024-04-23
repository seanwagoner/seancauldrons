from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    global_reset = """UPDATE global_inventory SET gold = 100, 
    num_potions = 0, 
    num_green_ml = 0, 
    num_blue_ml = 0, 
    num_red_ml = 0,
    num_dark_ml = 0,
    ml_threshold_large = 100,
    ml_threshold_normal = 200,
    ml_capacity = 10000
    """
    carts_reset = """DELETE FROM carts
    """
    cart_items_reset = """DELETE FROM cart_items
    """
    potions_reset = """UPDATE potions SET inventory = 0"""
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(global_reset))
        connection.execute(sqlalchemy.text(carts_reset))
        connection.execute(sqlalchemy.text(cart_items_reset))
        connection.execute(sqlalchemy.text(potions_reset))


    return "OK"

