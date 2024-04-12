from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    #when we are delivered potions, we use up part of our inventory
    #need to read in potions delivered, then update 
    sql_to_update = "UPDATE global_inventory SET num_green_ml = num_green_ml - :num_green_ml_used, num_green_potions = num_green_potions + :new_green_potions"

    new_green_potions = 0
    num_green_ml_used = 0
    for potion in potions_delivered:
        if potion.potion_type == [0, 100, 0, 0]:
            new_green_potions += potion.quantity
            num_green_ml_used += 100 * potion.quantity
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_to_update), {'num_green_ml_used': num_green_ml_used, 'new_green_potions': new_green_potions})


    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    sql_to_fetch = "SELECT num_green_ml from global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_fetch)).fetchone()
    num_green_ml = result[0]
    num_potions = num_green_ml // 100
    
    if num_potions:
        return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": num_potions,
            }
        ]
    else:
        return []


if __name__ == "__main__":
    print(get_bottle_plan())