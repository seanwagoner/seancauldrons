from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
@router.get("/audit")
def get_inventory():
    """Fetches inventory details including gold, milliliters in barrels, and number of potions."""
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
            SELECT gold, num_green_ml, num_blue_ml, num_red_ml, num_dark_ml, num_potions 
            FROM global_inventory
        """)).fetchone()
        

        gold, green_ml, blue_ml, red_ml, dark_ml, num_potions = result

        ml_in_barrels = green_ml + blue_ml + red_ml + dark_ml

    print(f"num_potions: {num_potions}, ml_in_barrels: {ml_in_barrels}, gold: {gold}\n")
    
    return {"number_of_potions": num_potions, "ml_in_barrels": ml_in_barrels, "gold": gold}



# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("""
            SELECT gold from global_inventory
            """)).fetchone()[0]
        curr_ml_capacity = connection.execute(sqlalchemy.text("""
            SELECT ml_capacity from global_inventory
            """)).fetchone()[0] // 10000
        curr_potion_capacity = connection.execute(sqlalchemy.text("""
            SELECT potion_capacity from global_inventory
            """)).fetchone()[0] // 50
        
        
        if gold >= 2100:
            potion_capacity = 1
            ml_capacity = 1
        elif gold >= 1100:
            if curr_ml_capacity >= curr_potion_capacity:
                potion_capacity = 1
            else:
                ml_capacity = 1
        

    return {
        "potion_capacity": potion_capacity,
        "ml_capacity": ml_capacity
    }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    gold_spent = 1000 * capacity_purchase.ml_capacity + capacity_purchase.potion_capacity
    new_potion_capacity = capacity_purchase.potion_capacity * 50
    new_ml_capacity = capacity_purchase.ml_capacity * 10000
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""
                                           UPDATE global_inventory SET 
                                           gold = gold - :gold_spent, 
                                           ml_capacity = ml_capacity + :new_ml_capacity,
                                           potion_capacity = potion_capacity + new_potion_capacity"""), 
                                           {"gold_spent" : gold_spent},
                                           {"new_ml_capacity" : new_ml_capacity},
                                           {"new_potion_capacity" : new_potion_capacity})

    return "OK"
