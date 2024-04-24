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
    new_green_potions = 0
    num_green_ml_used = 0
    new_red_potions = 0
    num_red_ml_used = 0
    new_blue_potions = 0
    num_blue_ml_used = 0
    new_dark_potions = 0
    num_dark_ml_used = 0
    new_purple_potions = 0
    new_yellow_potions = 0
    potions_added = 0
    
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            if potion.potion_type == [0, 100, 0, 0]:
                new_green_potions += potion.quantity
                num_green_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potions SET inventory = inventory + :new_green_potions WHERE item_sku = 'GREEN_POTION_0'"), {'new_green_potions' : new_green_potions})
            elif potion.potion_type == [100, 0, 0, 0]:
                new_red_potions += potion.quantity
                num_red_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potions SET inventory = inventory + :new_red_potions WHERE item_sku = 'RED_POTION_0'"), {'new_red_potions' : new_red_potions})
            elif potion.potion_type == [0, 0, 100, 0]:
                new_blue_potions += potion.quantity
                num_blue_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potions SET inventory = inventory + :new_blue_potions WHERE item_sku = 'BLUE_POTION_0'"), {'new_blue_potions' : new_blue_potions})
            elif potion.potion_type == [0, 0, 0, 100]:
                new_dark_potions += potion.quantity
                num_dark_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potions SET inventory = inventory + :new_dark_potions WHERE item_sku = 'DARK_POTION_0'"), {'new_dark_potions' : new_dark_potions})
            elif potion.potion_type == [50, 0, 50, 0]: 
                new_purple_potions += potion.quantity
                num_blue_ml_used += 50 * potion.quantity
                num_red_ml_used += 50 * potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potions SET inventory = inventory + :new_purple_potions WHERE item_sku = 'PURPLE_POTION_0'"), {'new_purple_potions' : new_purple_potions})
            elif potion.potion_type == [50, 50, 0, 0]:
                new_yellow_potions += potion.quantity
                num_red_ml_used += 50 * potion.quantity
                num_green_ml_used += 50 * potion.quantity
                connection.execute(sqlalchemy.text("UPDATE potions SET inventory = inventory + :new_yellow_potions WHERE item_sku = 'YELLOW_POTION_0'"), {'new_yellow_potions' : new_yellow_potions})
            potions_added += potion.quantity

        connection.execute(sqlalchemy.text("""UPDATE global_inventory SET num_green_ml = num_green_ml - :num_green_ml_used, 
                                           num_red_ml = num_red_ml - :num_red_ml_used, num_blue_ml = num_blue_ml - :num_blue_ml_used, num_dark_ml = num_dark_ml - :num_dark_ml_used"""), {'num_green_ml_used': 
                                           num_green_ml_used, 'num_red_ml_used': num_red_ml_used, 'num_blue_ml_used': num_blue_ml_used, 'num_dark_ml_used': num_dark_ml_used})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_potions = num_potions + :potions_added"), {'potions_added': 
                                           potions_added})
        

    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle by calculating how many potions can be made with the available ml.
    """
    potion_requirements = {
        "GREEN_POTION_0": [0, 100, 0, 0],
        "BLUE_POTION_0": [0, 0, 100, 0],
        "RED_POTION_0": [100, 0, 0, 0],
        "DARK_POTION_0": [0, 0, 0, 100],
        "PURPLE_POTION_0": [50, 0, 50, 0],  
        "YELLOW_POTION_0": [50, 50, 0, 0] 
    }

    result = []
    with db.engine.begin() as connection:
        colors = ["num_red_ml", "num_green_ml", "num_blue_ml", "num_dark_ml"]
        ml_available = {
            color: connection.execute(sqlalchemy.text(f"SELECT {color} FROM global_inventory")).scalar()
            for color in colors
        }
        
        for sku, ml_needs in potion_requirements.items():
            possible_quantities = [
                ml_available[ingredient] // need if need > 0 else float('inf')
                for ingredient, need in zip(colors, ml_needs)
            ]
            quantity = min(possible_quantities)

            if quantity > 0:
                result.append({"potion_type": ml_needs, "quantity": quantity})
                # Update available ml for each ingredient based on the potions made
                for idx, need in enumerate(ml_needs):
                    if need > 0:
                        ml_available[colors[idx]] -= quantity * need

    return result


if __name__ == "__main__":
    print(get_bottle_plan())