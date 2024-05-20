from fastapi import APIRouter

router = APIRouter()
import sqlalchemy
from src import database as db


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.connect() as connection:
        result = connection.execute(sqlalchemy.text(
                """
                SELECT p.item_sku, COALESCE(SUM(sle.change), 0) AS inventory, p.price, p.red, p.green, p.blue, p.dark
                FROM potions p
                LEFT JOIN supply_ledger_entries sle ON p.supply_id = sle.supply_id
                GROUP BY p.item_sku, p.price, p.red, p.green, p.blue, p.dark
                """
            )).fetchall()
        current_time = connection.execute(sqlalchemy.text("""
                            SELECT day, hour FROM time_table ORDER BY created_at DESC LIMIT 1;
                        """)).first()
        
        print(f"\nCurrent time: {current_time.day}  {current_time.hour}\n")
        
    catalog = []

    for column in result:
        potion_type = [column[3], column[4], column[5], column[6]]
        if column[1] > 0 and column[0] == "DARK_POTION_0":
            catalog.append({
                "sku": column[0], 
                "name": column[0].split('_')[0].lower() + " potion",  
                "quantity": column[1],
                "price": column[2],  
                "potion_type": potion_type
            })
        if column[1] > 0 and column[0] == "RAINBOW_POTION_0":
            catalog.append({
                "sku": column[0], 
                "name": column[0].split('_')[0].lower() + " potion",  
                "quantity": column[1],
                "price": column[2],  
                "potion_type": potion_type
            })
        
    for column in result:
        if len(catalog) >= 6:
            break
        potion_type = [column[3], column[4], column[5], column[6]]

        if any([((current_time.day == "Edgeday" and current_time.hour < 18) or (current_time.day == "Soulday" and current_time.hour >= 18)) and potion_type[0] == 100,
                ((current_time.day == "Bloomday" and current_time.hour < 18) or (current_time.day == "Edgeday" and current_time.hour >= 18)) and potion_type[1] == 100,
                ((current_time.day == "Arcanaday" and current_time.hour < 18) or (current_time.day == "Bloomday" and current_time.hour >= 18)) and potion_type[2] == 100]):
            print(f"It is {current_time.day} at {current_time.hour}. Not adding {column[0]} to catalog.\n")
            continue

        if potion_type == [50,50,0,0]:
            print(column[1])
        

        if column[1] > 0 and column[0] != "DARK_POTION_0" and column[0] != "RAINBOW_POTION_0":
            catalog.append({
                "sku": column[0], 
                "name": column[0].split('_')[0].lower() + " potion",  
                "quantity": column[1],
                "price": column[2],  
                "potion_type": potion_type
            })
        else:
            continue
        
        print(catalog)
    

    return catalog
    

