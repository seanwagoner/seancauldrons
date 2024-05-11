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
    new_white_potions = 0
    new_teal_potions = 0
    potions_added = 0
    
    with db.engine.begin() as connection:
        if potions_delivered:
            transaction_id = connection.execute(sqlalchemy.text("""INSERT INTO supply_transactions (description) 
                                                            VALUES ('Received potion(s).')
                                                            RETURNING id
                                                            """)).scalar()

        for potion in potions_delivered:
            if potion.potion_type == [0, 100, 0, 0]:
                new_green_potions += potion.quantity
                num_green_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 8, "transaction_id": transaction_id, "new_potions" : new_green_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:green_ml_id, :transaction_id, :green_ml)"""), 
                                                   {"green_ml_id" : 3, "transaction_id": transaction_id, "green_ml" : -num_green_ml_used})
                num_green_ml_used = 0
            elif potion.potion_type == [100, 0, 0, 0]:
                new_red_potions += potion.quantity
                num_red_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 7, "transaction_id": transaction_id, "new_potions" : new_red_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:red_ml_id, :transaction_id, :red_ml)"""), 
                                                   {"red_ml_id" : 2, "transaction_id": transaction_id, "red_ml" : -num_red_ml_used})
                num_red_ml_used = 0
            elif potion.potion_type == [0, 0, 100, 0]:
                new_blue_potions += potion.quantity
                num_blue_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 9, "transaction_id": transaction_id, "new_potions" : new_blue_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:blue_ml_id, :transaction_id, :blue_ml)"""), 
                                                   {"blue_ml_id" : 4, "transaction_id": transaction_id, "blue_ml" : -num_blue_ml_used})
                num_blue_ml_used = 0
            elif potion.potion_type == [0, 0, 0, 100]:
                new_dark_potions += potion.quantity
                num_dark_ml_used += 100 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change) 
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 10, "transaction_id": transaction_id, "new_potions" : new_dark_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:dark_ml_id, :transaction_id, :dark_ml)"""), 
                                                   {"dark_ml_id" : 5, "transaction_id": transaction_id, "dark_ml" : -num_dark_ml_used})
            elif potion.potion_type == [50, 0, 50, 0]: 
                new_purple_potions += potion.quantity
                num_blue_ml_used += 50 * potion.quantity
                num_red_ml_used += 50 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 11, "transaction_id": transaction_id, "new_potions" : new_purple_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:blue_ml_id, :transaction_id, :blue_ml)"""), 
                                                   {"blue_ml_id" : 4, "transaction_id": transaction_id, "blue_ml" : -num_blue_ml_used})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:red_ml_id, :transaction_id, :red_ml)"""), 
                                                   {"red_ml_id" : 2, "transaction_id": transaction_id, "red_ml" : -num_red_ml_used})
                num_red_ml_used = 0
                num_blue_ml_used = 0
            elif potion.potion_type == [50, 50, 0, 0]:
                new_yellow_potions += potion.quantity
                num_red_ml_used += 50 * potion.quantity
                num_green_ml_used += 50 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 12, "transaction_id": transaction_id, "new_potions" : new_yellow_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:red_ml_id, :transaction_id, :red_ml)"""), 
                                                   {"red_ml_id" : 2, "transaction_id": transaction_id, "red_ml" : -num_red_ml_used})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:green_ml_id, :transaction_id, :green_ml)"""), 
                                                   {"green_ml_id" : 3, "transaction_id": transaction_id, "green_ml" : -num_green_ml_used})
                num_red_ml_used = 0
                num_green_ml_used = 0
            elif potion.potion_type == [33, 34, 33, 0]:
                new_white_potions += potion.quantity
                num_red_ml_used += 50 * potion.quantity
                num_green_ml_used += 50 * potion.quantity
                num_blue_ml_used += 50 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 13, "transaction_id": transaction_id, "new_potions" : new_white_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:red_ml_id, :transaction_id, :red_ml)"""), 
                                                   {"red_ml_id" : 2, "transaction_id": transaction_id, "red_ml" : -num_red_ml_used})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:green_ml_id, :transaction_id, :green_ml)"""), 
                                                   {"green_ml_id" : 3, "transaction_id": transaction_id, "green_ml" : -num_green_ml_used})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:blue_ml_id, :transaction_id, :blue_ml)"""), 
                                                   {"blue_ml_id" : 4, "transaction_id": transaction_id, "blue_ml" : -num_blue_ml_used})
                num_red_ml_used = 0
                num_green_ml_used = 0
                num_blue_ml_used = 0
            elif potion.potion_type == [0, 50, 50, 0]:
                new_teal_potions += potion.quantity
                num_blue_ml_used += 50 * potion.quantity
                num_green_ml_used += 50 * potion.quantity
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:potion_id, :transaction_id, :new_potions)"""), 
                                                   {"potion_id" : 14, "transaction_id": transaction_id, "new_potions" : new_teal_potions})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:blue_ml_id, :transaction_id, :blue_ml)"""), 
                                                   {"blue_ml_id" : 4, "transaction_id": transaction_id, "blue_ml" : -num_blue_ml_used})
                connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                                                   VALUES (:green_ml_id, :transaction_id, :green_ml)"""), 
                                                   {"green_ml_id" : 3, "transaction_id": transaction_id, "green_ml" : -num_green_ml_used})
                num_green_ml_used = 0
                num_blue_ml_used = 0

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
        "YELLOW_POTION_0": [50, 50, 0, 0],
        "TEAL_POTION_0": [0, 50, 50, 0],
        "WHITE_POTION_0": [33, 34, 33, 0],
    }

    potion_amounts = {
        "red": 0,
        "green" : 0,
        "blue" : 0,
        "dark" : 0,
        "purple" : 0,
        "yellow" : 0
    }
    
    result = []
    with db.engine.begin() as connection:

        num_red_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 2}).scalar()
        num_green_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 3}).scalar()
        num_blue_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 4}).scalar()
        num_dark_ml = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 5}).scalar()                      

        red_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 7}).scalar()
        green_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 8}).scalar()
        blue_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 9}).scalar()
        dark_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 10}).scalar()
        purple_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 11}).scalar()
        yellow_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 12}).scalar()
        white_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 13}).scalar()
        teal_potions = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS balance FROM supply_ledger_entries
                                           WHERE supply_id = :supply_id"""), {"supply_id" : 14}).scalar()
        
        print(f"current red potions: {red_potions}, current blue_potions: {blue_potions}, current green_potions: {green_potions}")
        print(f"current purple potions: {purple_potions}, current yellow_potions: {yellow_potions}")
        print(f"current dark potions: {dark_potions}, current white_potions: {white_potions}, current teal_potions: {teal_potions}")

        print(f"red_ml: {num_red_ml}, blue_ml: {num_blue_ml}, green_ml: {num_green_ml}, dark_ml: {num_dark_ml}")

        potion_limit = connection.execute(sqlalchemy.text("""SELECT potion_capacity FROM global_inventory""")).fetchone()[0]

        current_potions = red_potions + green_potions + blue_potions + dark_potions + purple_potions + yellow_potions + white_potions + teal_potions
        new_red_potions = 0
        new_green_potions = 0
        new_blue_potions = 0
        new_purple_potions = 0
        new_yellow_potions = 0
        new_dark_potions = 0
        new_white_potions = 0
        new_teal_potions = 0

        print(f"max red potions: {num_red_ml // 100}, max green potions: {num_green_ml // 100}, max blue: {num_blue_ml // 100}, max dark: {num_dark_ml // 100}")

        while current_potions < potion_limit:
            if num_red_ml >= 100 and (red_potions + new_red_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_red_potions += 1
                num_red_ml -= 100
                current_potions += 1
            if num_green_ml >= 100 and (green_potions + new_green_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_green_potions += 1
                num_green_ml -= 100
                current_potions += 1
            if num_blue_ml >= 100 and (blue_potions + new_blue_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_blue_potions += 1
                num_blue_ml -= 100
                current_potions += 1
            if num_dark_ml >= 100 and (dark_potions + new_dark_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_dark_potions += 1
                num_dark_ml -= 100
                current_potions += 1
            if num_red_ml >= 50 and num_blue_ml >= 50 and (purple_potions + new_purple_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_purple_potions += 1
                num_red_ml -= 50
                num_blue_ml -= 50
                current_potions += 1
            if num_red_ml >= 50 and num_green_ml >= 50 and (yellow_potions + new_yellow_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_yellow_potions += 1
                num_red_ml -= 50
                num_green_ml -= 50
                current_potions += 1
            if num_blue_ml >= 50 and num_green_ml >= 50 and (teal_potions + new_teal_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_teal_potions += 1
                num_blue_ml -= 50
                num_green_ml -= 50
                current_potions += 1
            if num_red_ml >= 33 and num_green_ml >= 34 and num_blue_ml >= 33 and (white_potions + new_white_potions) < int(potion_limit / 4) and current_potions < potion_limit:
                new_white_potions += 1
                num_red_ml -= 33
                num_green_ml -= 34
                num_blue_ml -= 33
                current_potions += 1
            else:
                break

        while current_potions > potion_limit:
            new_red_potions -= 1
            current_potions -= 1
        
        print(f"limit: {potion_limit}")
        print(f"current potions: {current_potions}")
        
        print(f"red_ml after: {num_red_ml}, blue_ml: {num_blue_ml}, green_ml: {num_green_ml}, dark_ml: {num_dark_ml}")

        if new_red_potions > 0:
            result.append({"potion_type": potion_requirements["RED_POTION_0"], "quantity": new_red_potions})
        if new_green_potions > 0:
            result.append({"potion_type": potion_requirements["GREEN_POTION_0"], "quantity": new_green_potions})
        if new_blue_potions > 0:
            result.append({"potion_type": potion_requirements["BLUE_POTION_0"], "quantity": new_blue_potions})
        if new_yellow_potions > 0:
            result.append({"potion_type": potion_requirements["PURPLE_POTION_0"], "quantity": new_yellow_potions})
        if new_purple_potions > 0:
            result.append({"potion_type": potion_requirements["YELLOW_POTION_0"], "quantity": new_purple_potions})
        if new_dark_potions > 0:
            result.append({"potion_type": potion_requirements["DARK_POTION_0"], "quantity": new_dark_potions})
        if new_white_potions > 0:
            result.append({"potion_type": potion_requirements["WHITE_POTION_0"], "quantity": new_white_potions})
        if new_teal_potions > 0:
            result.append({"potion_type": potion_requirements["TEAL_POTION_0"], "quantity": new_teal_potions})
    print(result)
    return result


if __name__ == "__main__":
    print(get_bottle_plan())