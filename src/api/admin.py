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
    sql_update_gold = "UPDATE global_inventory SET gold = 100"
    sql_update_potions = "UPDATE global_inventory SET num_green_potions = 0, num_blue_potions = 0, num_red_potions = 0"
    sql_update_ml = "UPDATE global_inventory SET num_green_ml = 0, num_blue_ml = 0, num_red_ml = 0"
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_update_gold))
        connection.execute(sqlalchemy.text(sql_update_potions))
        connection.execute(sqlalchemy.text(sql_update_ml))


    return "OK"

