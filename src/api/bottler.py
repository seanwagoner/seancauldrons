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
    green_update = "UPDATE global_inventory SET num_green_ml = num_green_ml - :num_green_ml_used, num_green_potions = num_green_potions + :new_green_potions"
    red_update = "UPDATE global_inventory SET num_red_ml = num_red_ml - :num_red_ml_used, num_red_potions = num_red_potions + :new_red_potions"
    blue_update = "UPDATE global_inventory SET num_blue_ml = num_blue_ml - :num_blue_ml_used, num_blue_potions = num_blue_potions + :new_blue_potions"

    new_green_potions = 0
    num_green_ml_used = 0
    new_red_potions = 0
    num_red_ml_used = 0
    new_blue_potions = 0
    num_blue_ml_used = 0

    for potion in potions_delivered:
        if potion.potion_type == [0, 100, 0, 0]:
            new_green_potions += potion.quantity
            num_green_ml_used += 100 * potion.quantity
        if potion.potion_type == [100, 0, 0, 0]:
            new_red_potions += potion.quantity
            num_red_ml_used += 100 * potion.quantity
        if potion.potion_type == [0, 0, 100, 0]:
            new_blue_potions += potion.quantity
            num_blue_ml_used += 100 * potion.quantity
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(green_update), {'num_green_ml_used': num_green_ml_used, 'new_green_potions': new_green_potions})
        connection.execute(sqlalchemy.text(red_update), {'num_red_ml_used': num_red_ml_used, 'new_red_potions': new_red_potions})
        connection.execute(sqlalchemy.text(blue_update), {'num_blue_ml_used': num_blue_ml_used, 'new_blue_potions': new_blue_potions})

    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        num_green_ml = (connection.execute(sqlalchemy.text("SELECT num_green_ml from global_inventory")).fetchone())[0]
        num_green_potions = num_green_ml // 100
        num_blue_ml = (connection.execute(sqlalchemy.text("SELECT num_blue_ml from global_inventory")).fetchone())[0]
        num_blue_potions = num_blue_ml // 100
        num_red_ml = (connection.execute(sqlalchemy.text("SELECT num_blue_ml from global_inventory")).fetchone())[0]
        num_red_potions = num_red_ml // 100
    
    result = []
    if num_green_potions:
        result.append([
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": num_green_potions,
            }
        ])
    elif num_blue_potions:
        result.append([
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": num_blue_potions,
            }
        ])
    elif num_red_potions:
        result.append([
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_red_potions,
            }
        ])

    return result


if __name__ == "__main__":
    print(get_bottle_plan())