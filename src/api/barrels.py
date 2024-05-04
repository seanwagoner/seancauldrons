from sqlite3 import IntegrityError
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import random

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
    with db.engine.begin() as connection:
        gold_paid = 0
        red_ml = 0
        green_ml = 0
        blue_ml = 0
        dark_ml = 0

        if barrels_delivered:
            transaction_id = connection.execute(sqlalchemy.text("""INSERT INTO supply_transactions (description) 
                                                            VALUES ('Purchased barrel(s).')
                                                            RETURNING id
                                                            """)).scalar()

        for barrel_delivered in barrels_delivered:
            gold_paid -= barrel_delivered.price * barrel_delivered.quantity
            if barrel_delivered.potion_type == [1, 0, 0, 0]:
                red_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:red_ml_id, :transaction_id, :red_ml)"""), 
                                                   {"red_ml_id" : 2, "transaction_id": transaction_id, "red_ml" : red_ml})
            elif barrel_delivered.potion_type == [0, 1, 0, 0]:
                green_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:green_ml_id, :transaction_id, :green_ml)"""), 
                                                   {"green_ml_id" : 3, "transaction_id": transaction_id, "green_ml" : green_ml})
            elif barrel_delivered.potion_type == [0, 0, 1, 0]:
                blue_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:blue_ml_id, :transaction_id, :blue_ml)"""), 
                                                   {"blue_ml_id" : 4, "transaction_id": transaction_id, "blue_ml" : blue_ml})
            elif barrel_delivered.potion_type == [0, 0, 0, 1]:
                dark_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:dark_ml_id, :transaction_id, :dark_ml)"""), 
                                                   {"dark_ml_id" : 5, "transaction_id": transaction_id, "red_ml" : dark_ml})
            else:
                raise Exception("Invalid potion type")
            
        gold = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :gold_id"""), {"gold_id" : 1}).fetchone()[0]
        
        print("current gold: ", gold)
        
        print(f"gold_paid: {gold_paid}, red_ml: {red_ml}, green_ml: {green_ml}, blue_ml: {blue_ml}, dark_ml: {dark_ml}")
    
        print("TRANSACTION ID: ", transaction_id)

        #adding ledger entry
        connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                            VALUES (:gold_id, :transaction_id, :gold_paid)"""), 
                            {"gold_id" : 1, "transaction_id": transaction_id, "gold_paid" : gold_paid})

    print(f"barrels delivered: {barrels_delivered} order_id: {order_id} transaction_id: {transaction_id}")

    return "OK"

def calculate_barrel_to_purchase(catalog, gold, type, ml):
    best_option = None
    max_effectiveness = 0 

    color = type.index(1)
    for barrel in catalog:
        if barrel.potion_type[color]:
            max_quantity = min(gold // barrel.price, ml // barrel.ml_per_barrel)
            if max_quantity > 0:
                effectiveness = barrel.ml_per_barrel / barrel.price
                if effectiveness > max_effectiveness:
                    max_effectiveness = effectiveness
                    best_option = {
                        'sku': barrel.sku,
                        'quantity': int(max_quantity),
                        'total_ml': barrel.ml_per_barrel * max_quantity,
                        'total_cost': barrel.price * max_quantity
                    }

    return best_option

@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(f"barrel catalog: {wholesale_catalog}")
    
    with db.engine.begin() as connection:


        
        result = (connection.execute(sqlalchemy.text("""SELECT
                                                    ml_threshold_normal,
                                                    ml_threshold_large,
                                                    ml_capacity
                                                    FROM global_inventory"""))).fetchone()
    
        gold = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :gold_id"""), {"gold_id" : 1}).fetchone()[0]
        num_red_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :red_ml_id"""), {"red_ml_id" : 2}).fetchone()[0]
        num_green_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :green_ml_id"""), {"green_ml_id" : 3}).fetchone()[0]
        num_blue_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :blue_ml_id"""), {"blue_ml_id" : 4}).fetchone()[0]
        num_dark_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :dark_ml_id"""), {"dark_ml_id" : 5}).fetchone()[0]
    ml_threshold_normal = result[0]
    ml_threshold_large = result[1]
    MAX_ML = result[2]
    ml_inventory = [num_green_ml, num_red_ml, num_blue_ml, num_dark_ml]
    current_ml = sum(ml_inventory)

    purchase_plan = []

    selling_large = any(item.sku.startswith('LARGE') for item in wholesale_catalog)

    threshold = ml_threshold_large if selling_large else ml_threshold_normal
    for i, ml in enumerate(ml_inventory):
        if ml < threshold:
            potion_type = [int(j == i) for j in range(4)]
            barrel_purchase = calculate_barrel_to_purchase(wholesale_catalog, gold // 4 if gold > 300 else gold, potion_type, MAX_ML - current_ml)
            if barrel_purchase:
                price = next(item.price for item in wholesale_catalog if item.sku == barrel_purchase['sku'])
                ml_per_barrel = next(item.ml_per_barrel for item in wholesale_catalog if item.sku == barrel_purchase['sku'])
                purchase_plan.append(barrel_purchase)
                gold -= price * barrel_purchase['quantity']
                current_ml += ml_per_barrel * barrel_purchase['quantity']

    

    return purchase_plan


