from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

# purchase a new small green potion barrel
# only if num of potions in inventory is < 10

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    total_cost = sum(barrel.price * barrel.quantity for barrel in barrels_delivered)
    total_ml_green = sum(barrel.ml_per_barrel * barrel.quantity for barrel in barrels_delivered if barrel.potion_type == [0, 1, 0, 0])

    sql_update_gold = "UPDATE global_inventory SET gold = gold - :total_cost"
    sql_update_green_ml = "UPDATE global_inventory SET num_green_ml = num_green_ml + :total_ml_green"


    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(sql_update_gold), {'total_cost': total_cost})
        connection.execute(sqlalchemy.text(sql_update_green_ml), {'total_ml_green': total_ml_green})

    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    sql_to_execute = "SELECT num_green_potions, gold FROM global_inventory"
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(sql_to_execute)).fetchone()
    
    num_green_potions, gold = result
    
    purchase_plan = []
    for barrel in wholesale_catalog:
        if barrel.potion_type == [0, 1, 0, 0] and num_green_potions < 10 and gold >= barrel.price:
            quantity_to_buy = min((10 - num_green_potions), gold // barrel.price)
            purchase_plan.append({"sku": barrel.sku, "quantity": quantity_to_buy})
            break

    return purchase_plan

