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
def get_inventory():
    """Fetches gold inventory"""
    gold_query = "SELECT gold FROM global_inventory"
    barrel_query = "SELECT num_green_ml FROM global_inventory"
    potion_query = "SELECT num_green_potions FROM global_inventory"
    with db.engine.begin() as connection:
        gold_table = connection.execute(sqlalchemy.text(gold_query))
        for row in gold_table:
            gold = row[0]
        barrel_table = connection.execute(sqlalchemy.text(barrel_query))
        for row in barrel_table:
            ml_in_barrels = row[0]
        potion_table = connection.execute(sqlalchemy.text(potion_query))
        for row in potion_table:
            number_of_potions = row[0]
    
    return {"number_of_potions": number_of_potions, "ml_in_barrels": ml_in_barrels, "gold": gold}


# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
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

    return "OK"
