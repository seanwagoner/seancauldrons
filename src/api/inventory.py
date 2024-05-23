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
        gold = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 1}).scalar()
        red_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 2}).scalar()
        green_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 3}).scalar()
        blue_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 4}).scalar()
        dark_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 5}).scalar()  
        
        red_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 7}).scalar()  
        green_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 8}).scalar()  
        blue_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 9}).scalar()  
        dark_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 10}).scalar()  
        purple_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 11}).scalar()  
        yellow_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 12}).scalar()
        white_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 13}).scalar()
        teal_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 14}).scalar()
        rainbow_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 15}).scalar()
        orange_potion = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 16}).scalar()

        num_potions = orange_potion + rainbow_potion + red_potion + green_potion + blue_potion + dark_potion + purple_potion + yellow_potion + white_potion + teal_potion

        ml_in_barrels = green_ml + blue_ml + red_ml + dark_ml
    
    print("--------------------------------------------------------------------------------")
    print("BARRELS: \n")
    print(f"RED: {red_ml}, GREEN: {green_ml}, BLUE: {blue_ml}, DARK: {dark_ml}")
    print("--------------------------------------------------------------------------------")
    print("POTIONS: \n")
    print(f"RED: {red_potion}, GREEN: {green_potion}, BLUE: {blue_potion}, DARK: {dark_potion}")
    print(f"PURPLE: {purple_potion}, YELLOW: {yellow_potion}, WHITE: {white_potion}, TEAL: {teal_potion}")
    print(f"RAINBOW: {rainbow_potion}, ORANGE: {orange_potion}")
    print("--------------------------------------------------------------------------------")
    print("QUANTITIES: \n")
    print(f"TOTAL POTIONS: {num_potions} || TOTAL ML: {ml_in_barrels} || GOLD: {gold}\n")
    
    return {"number_of_potions": num_potions, "ml_in_barrels": ml_in_barrels, "gold": gold}



# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 1}).scalar()
        curr_ml_capacity = connection.execute(sqlalchemy.text("""
            SELECT ml_capacity from global_inventory
            """)).fetchone()[0] // 10000
        curr_potion_capacity = connection.execute(sqlalchemy.text("""
            SELECT potion_capacity from global_inventory
            """)).fetchone()[0] // 50
        
        potion_capacity = 0
        ml_capacity = 0
        
        if gold >= 2100:
            potion_capacity += 1
            ml_capacity += 1
        elif gold >= 1100:
            if curr_ml_capacity >= curr_potion_capacity:
                potion_capacity += 1

            else:
                ml_capacity += 1
        

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
    with db.engine.begin() as connection:
        if capacity_purchase.potion_capacity or capacity_purchase.ml_capacity:
            gold_spent = (1000 * capacity_purchase.ml_capacity) + (1000 * capacity_purchase.potion_capacity)
            new_potion_capacity = capacity_purchase.potion_capacity * 50
            new_ml_capacity = capacity_purchase.ml_capacity * 10000
            print(gold_spent)
            transaction_id = connection.execute(sqlalchemy.text("""INSERT INTO supply_transactions (description) 
                                                            VALUES ('Purchased capacity upgrade.')
                                                            RETURNING id
                                                            """)).scalar()
            print(transaction_id)
            connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                    VALUES (:gold_id, :transaction_id, :gold_spent)"""), 
                                                   {"gold_id" : 1, "transaction_id": transaction_id, "gold_spent" : -gold_spent})
            connection.execute(sqlalchemy.text("""
                                                UPDATE global_inventory SET 
                                                ml_capacity = ml_capacity + :new_ml_capacity,
                                           potion_capacity = potion_capacity + :new_potion_capacity"""), 
                                           {"new_ml_capacity" : new_ml_capacity,
                                           "new_potion_capacity" : new_potion_capacity})
    

    print("added potion cap: ", new_potion_capacity)
    print("added ml cap: ", new_ml_capacity)


    return "OK"
