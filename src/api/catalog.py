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
        
    catalog = []
    for column in result:
        potion_type = [column[3], column[4], column[5], column[6]]
        if potion_type == [25, 25, 25, 25] and column[1] > 0:
            print("adding rainbow")
            rainbow_potion = {
                "sku": column[0],
                "name": column[0].split('_')[0].lower() + " potion",
                "quantity": column[1],
                "price": column[2],
                "potion_type": potion_type
            }
            if column[1] > 0:
                catalog.append(rainbow_potion)

    for column in result:
        if len(catalog) >= 6:
            break
        potion_type = [column[3], column[4], column[5], column[6]]


        if column[1] > 0 and column[0] != "RAINBOW_POTION_0":
            catalog.append({
                "sku": column[0], 
                "name": column[0].split('_')[0].lower() + " potion",  
                "quantity": column[1],
                "price": column[2],  
                "potion_type": potion_type
            })
        
        print(catalog)
    

    return catalog
    

