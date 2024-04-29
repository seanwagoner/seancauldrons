from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db


router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    #don't do this yet
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    with db.engine.begin() as connection:
        for customer in customers:
            connection.execute(sqlalchemy.text(
                "INSERT INTO customers (name, class, level) VALUES (:name, :class, :level)"
            ), {'name': customer.customer_name, 'class': customer.character_class, 'level': customer.level})


    return "OK"

@router.post("/")
def create_cart():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("INSERT INTO carts DEFAULT VALUES RETURNING id"))
        cart_id = result.fetchone()[0]
    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        cart_exists = connection.execute(sqlalchemy.text("SELECT id FROM carts WHERE id = :cart_id"), {'cart_id': cart_id}).scalar()
        if not cart_exists:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        potion_id = connection.execute(sqlalchemy.text(
            "SELECT id FROM potions WHERE item_sku = :item_sku"
        ), {'item_sku': item_sku}).fetchone()[0]

        item_exists = connection.execute(sqlalchemy.text(
            "SELECT 1 FROM cart_items WHERE cart_id = :cart_id AND potion_id = :potion_id"
        ), {'cart_id': cart_id, 'potion_id': potion_id}).scalar()

        if item_exists:
            raise HTTPException(status_code=400, detail="Item already exists in the cart")

        connection.execute(sqlalchemy.text(
            "INSERT INTO cart_items (cart_id, potion_id, quantity) VALUES (:cart_id, :potion_id, :quantity)"
        ), {'cart_id': cart_id, 'potion_id': potion_id, 'quantity': cart_item.quantity})

    
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    with db.engine.begin() as connection:
        cart_items = connection.execute(sqlalchemy.text(
            "SELECT potion_id, quantity FROM cart_items WHERE cart_id = :cart_id"
        ), {'cart_id': cart_id}).fetchall()
        
        total_potions_bought = 0

        for item in cart_items:
            potion_id = item[0]
            quantity = item[1]

            connection.execute(sqlalchemy.text(
                "UPDATE potions SET inventory = inventory - :quantity WHERE id = :potion_id AND inventory >= :quantity"
            ), {'quantity': quantity, 'potion_id': potion_id})

            total_potions_bought += quantity

        profit = 50 * total_potions_bought


        connection.execute(sqlalchemy.text(
            "UPDATE global_inventory SET gold = gold + :profit, num_potions = num_potions - :total_potions_bought"
        ), {'profit': profit, 'total_potions_bought': total_potions_bought})

        connection.execute(sqlalchemy.text(
            "DELETE FROM cart_items WHERE cart_id = :cart_id"
        ), {'cart_id': cart_id})
        
        connection.execute(sqlalchemy.text(
            "DELETE FROM carts WHERE id = :cart_id"
        ), {'cart_id': cart_id})
    
    print({"total_potions_bought": total_potions_bought, "total_gold_paid": profit})
    
    return {"total_potions_bought": total_potions_bought, "total_gold_paid": profit}

    
