from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials

from src.App.Auth_utils import get_user_from_credentials, require_account_type
from src.App.JWTBearer import JWTBearer
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.UserDAO import UserDAO
from src.Model.Order import Order
from src.Service.CustomerService import CustomerService

from .init_app import user_service

customer_router = APIRouter(
    prefix="/customer", tags=["Customer"], dependencies=[Depends(require_account_type("Customer"))]
)

customer_service = CustomerService()


db_connector = DBConnector()
customer_dao = CustomerDAO(db_connector)
user_dao = UserDAO(db_connector)


active_carts = {}


def get_cart_for_user(username: str) -> dict:
    """Function that returns the active cart of a customer.

    Parameters
    ----------
    username: str
        user's username

    Returns
    -------
    dict
        Returns the user's cart.
    """
    print(f"Fetching cart for {username}")
    cart = active_carts.get(username, {})
    print(f"Cart for {username}: {cart}")
    return cart


@customer_router.get("/Menu", status_code=status.HTTP_201_CREATED)
def View_menu() -> List[dict]:
    """If you want to see the EJR's current menu."""
    try:
        menu = customer_service.view_menu()
        print("menu fetched:", menu)
        return menu
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@customer_router.post("/Add_to_Cart", status_code=status.HTTP_200_OK)
def add_items_to_cart(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
    item: Annotated[List[str], Query(description="Item name")],
    quantities: Annotated[List[int], Query(description="Quantity for each item")],
) -> dict:
    """If you want to add an item to your cart."""
    customer = get_user_from_credentials(credentials)
    username_customer = customer.username
    cart = get_cart_for_user(username_customer)
    print(f"Cart before adding items: {cart}")
    if cart is None:
        cart = {}
    if len(item) != len(quantities):
        return {"error": "Items and quantities must match"}
    try:
        cart = customer_service.add_item_cart(username_customer, cart, item, quantities)
        active_carts[username_customer] = cart
        return cart
        print(f"Cart after adding items: {cart}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@customer_router.post("/Modify_Cart", status_code=status.HTTP_200_OK)
def Modify_cart(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())], name_item: str, new_quantity: int
) -> dict:
    """If you want to change an item's quantity from your cart."""
    customer = get_user_from_credentials(credentials)
    username_customer = customer.username
    cart = get_cart_for_user(username_customer)
    try:
        cart = customer_service.modify_cart(cart, name_item, new_quantity)
        active_carts[username_customer] = cart
        return cart
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@customer_router.get("/View_Cart", status_code=status.HTTP_200_OK)
def View_cart(credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]):
    """If you want to see your current cart."""
    customer = get_user_from_credentials(credentials)
    username_customer = customer.username
    cart = get_cart_for_user(username_customer)
    try:
        cart = customer_service.view_cart(cart)
        return cart
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@customer_router.post("/Validate_Cart", status_code=status.HTTP_200_OK)
def Validate_cart(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
    validate: Literal["yes", "no"],
    address: Optional[str] = None,
) -> str:
    """If you want to validate your cart and place an order."""
    username = get_user_from_credentials(credentials).username
    customer = customer_dao.find_by_username(username)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with username {username} not found.")
    username_customer = customer.username
    if address is None:
        address = customer.address

    cart = get_cart_for_user(username_customer)
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty or not found.")
    try:
        order = customer_service.validate_cart(cart, username_customer, validate, address)
        return f"Your cart has been validated. The order has been created: {order}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@customer_router.get("/View_Order", status_code=status.HTTP_200_OK)
def View_order(credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]) -> Order:
    """If you want to see your order."""
    customer = get_user_from_credentials(credentials)
    username_customer = customer.username
    try:
        order = customer_service.view_order(username_customer)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@customer_router.patch("/Edit_Profile", status_code=status.HTTP_200_OK)
def Edit_Profile(
    firstname: Optional[str] = Query(None, description="First name"),
    lastname: Optional[str] = Query(None, description="Last name"),
    password: Optional[str] = Query(None, description="Password"),
    address: Optional[str] = Query(None, description="Postal address"),
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())] = None,
) -> dict:
    """If you want to edit your own profile."""

    username = get_user_from_credentials(credentials).username
    try:
        customer = customer_dao.update_customer(username, address)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=403, detail=f"Error updating profile: {error}") from error

    try:
        user = user_service.update_user(username, firstname, lastname, password)
    except Exception as error:
        raise HTTPException(status_code=403, detail=f"Error updating profile: {error}") from error

    return {
        "detail": "Profile updated successfully",
        "firstname": user.firstname,
        "lastname": user.lastname,
        "address": customer.address,
    }
