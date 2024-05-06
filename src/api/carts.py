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

    items_per_page = 5
    offset = search_page * items_per_page

    columns = [
        db.cart_items.c.id.label("line_item_id"),
        db.potions.c.item_sku,
        db.customers.c.name.label("customer_name"),
        (db.cart_items.c.quantity * db.potions.c.price).label("line_item_total"),
        db.cart_items.c.timestamp
    ]

    stmt = sqlalchemy.select(columns).select_from(
        db.cart_items
        .join(db.carts, db.cart_items.c.cart_id == db.carts.c.id)
        .join(db.customers, db.carts.c.customer_id == db.customers.c.id)
        .join(db.potions, db.cart_items.c.potion_id == db.potions.c.id)
    )

    if customer_name:
        stmt = stmt.where(db.customers.c.name.ilike(f"%{customer_name.lower()}%"))
    if potion_sku:
        stmt = stmt.where(db.potions.c.item_sku.ilike(f"%{potion_sku.lower()}%"))

    if sort_col == search_sort_options.customer_name:
        order_by = db.customers.c.name
    elif sort_col == search_sort_options.item_sku:
        order_by = db.potions.c.item_sku
    elif sort_col == search_sort_options.line_item_total:
        order_by = (db.cart_items.c.quantity * db.potions.c.price)
    else:
        order_by = db.cart_items.c.timestamp
    if sort_order == search_sort_order.desc:
        order_by = sqlalchemy.desc(order_by)

    stmt = stmt.order_by(order_by, db.cart_items.c.id).limit(items_per_page).offset(offset)

    with db.engine.connect() as conn:
        results = conn.execute(stmt).fetchall()

    formatted_results = [{
        "line_item_id": row.line_item_id,
        "item_sku": row.item_sku,
        "customer_name": row.customer_name,
        "line_item_total": row.line_item_total,
        "timestamp": row.timestamp.isoformat(),
    } for row in results]

    previous_page = search_page - 1 if search_page > 0 else None
    next_page = search_page + 1 if len(results) == items_per_page else None

    return {
        "previous": previous_page,
        "next": next_page,
        "results": formatted_results
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

        connection.execute(sqlalchemy.text(
            "INSERT INTO cart_items (cart_id, potion_id, quantity) VALUES (:cart_id, :potion_id, :quantity)"
        ), {'cart_id': cart_id, 'potion_id': potion_id, 'quantity': cart_item.quantity})

    
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    with db.engine.begin() as connection:
        profit = 0
        total_potions_bought = 0
        cart_items = connection.execute(sqlalchemy.text(
            """SELECT ci.potion_id, ci.quantity, p.supply_id, p.price
            FROM cart_items ci
            JOIN potions p ON ci.potion_id = p.id
            WHERE ci.cart_id = :cart_id
            """
        ), {'cart_id': cart_id}).fetchall()
        
        transaction_id = connection.execute(sqlalchemy.text("""INSERT INTO supply_transactions (description) 
                                                            VALUES ('Customer of cart_id :cart_id purchased potions.')
                                                            RETURNING id
                                                            """), {"cart_id" : cart_id}).scalar()

        for item in cart_items:
            potion_id = item[0]
            quantity = item[1]
            supply_id = item[2]
            price = item[3]

            print(f"Potion ID: {potion_id}, Quantity: {quantity}, Supply ID: {supply_id}, Price: {price}")

            connection.execute(sqlalchemy.text(
                """INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                VALUES (:supply_id, :transaction_id, :change)
                """
            ), {'supply_id': supply_id, 'transaction_id': transaction_id, 'change': -quantity})

            profit += price * quantity

            total_potions_bought += quantity
        
        connection.execute(sqlalchemy.text("""INSERT INTO supply_ledger_entries (supply_id, supply_transaction_id, change)
                            VALUES
                            (:gold_id, :transaction_id, :gold_paid)
                            """), 
                            {"gold_id" : 1, "transaction_id": transaction_id, "gold_paid" : profit},
                            )

        connection.execute(sqlalchemy.text(
            "DELETE FROM cart_items WHERE cart_id = :cart_id"
        ), {'cart_id': cart_id})
        
        connection.execute(sqlalchemy.text(
            "DELETE FROM carts WHERE id = :cart_id"
        ), {'cart_id': cart_id})
    
    print({"total_potions_bought": total_potions_bought, "total_gold_paid": profit})
    
    return {"total_potions_bought": total_potions_bought, "total_gold_paid": profit}

    
