from __future__ import annotations

from typing import Annotated, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials

from src.App.Auth_utils import get_user_from_credentials, require_account_type
from src.App.JWTBearer import JWTBearer
from src.Model.APIUser import APIUser
from src.Model.User import User
from src.Service.PasswordService import check_password_strength

from .init_app import (
    admin_service,
    customer_repo,
    driver_repo,
    google_map_service,
    item_repo,
    item_service,
    user_repo,
    user_service,
)

administrator_router = APIRouter(
    prefix="/administrator", tags=["Administrator"], dependencies=[Depends(require_account_type("Administrator"))]
)


@administrator_router.post("/Create_Accounts", status_code=status.HTTP_201_CREATED)
def Create_Accounts(
    username: str,
    password: str,
    firstname: str,
    lastname: str,
    account_type: Literal["Administrator", "DeliveryDriver", "Customer"],
) -> APIUser:
    """If you want to create a customer, delivery driver or administrator account."""
    try:
        check_password_strength(password=password)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Password too weak") from e
    try:
        user: User = admin_service.create_user(
            username=username.lower(),
            password=password,
            firstname=firstname,
            lastname=lastname,
            account_type=account_type,
        )
    except Exception as error:
        raise HTTPException(status_code=409, detail=f"{error}") from error
    return APIUser(username=user.username, account_type=account_type)


@administrator_router.patch("/Edit_Accounts", status_code=status.HTTP_200_OK)
def Edit_Accounts(
    username: str, attribute: Literal["firstname", "lastname", "address", "vehicle"], new_value: str
) -> dict:
    """If you want to edit another profile's attribute such as names for example."""
    if attribute == "address":
        if user_service.get_user(username).account_type != "Customer":
            raise ValueError("Only customers have an address.")
        google_map_service.geocoding_address(new_value)
        customer_repo.update_customer(username, new_value)
    if attribute == "vehicle":
        if user_service.get_user(username).account_type != "DeliveryDriver":
            raise ValueError("Only delivery drivers have a vehicle.")
        if new_value not in ("walking", "cycling", "driving"):
            raise ValueError("Vehicle not accepted. Values accepted : 'walking', 'cycling' or 'driving'.")
        driver_repo.update_delivery_driver(username, vehicle=new_value)
    if attribute == "firstname":
        user_repo.update_user(username, firstname=new_value)
    if attribute == "lastname":
        user_repo.update_user(username, lastname=new_value)
    return {
        "detail": "Account updated successfully",
    }


@administrator_router.delete("/Delete_User", status_code=status.HTTP_200_OK)
def Delete_User(username) -> bool:
    """If you want to delete another user's account."""
    try:
        user_deleted = user_service.delete_user(username)
        return user_deleted
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@administrator_router.get("/Storage/View", status_code=status.HTTP_200_OK)
def View_Storage() -> dict:
    """If you want to see the whole EJR current storage."""
    try:
        storage = item_service.view_storage()
        print("Storage fetched:", storage)
        return storage
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@administrator_router.post("/Storage/Create_Item", status_code=status.HTTP_201_CREATED)
def Create_Item(
    name_item: str,
    price: float,
    stock: int,
    category: str = Query(..., description="Type of item", enum=["starter", "main course", "dessert", "drink"]),
) -> dict:
    """If you want to create a new item."""
    try:
        new_item = item_service.create_item(name_item, int(price * 100), category, stock)
        return {"message": "Item created successfully ", "item": new_item}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@administrator_router.patch("/Storage/Edit_Item", status_code=status.HTTP_200_OK)
def Edit_Item(
    name_item,
    new_name: str = None,
    new_price: float = None,
    new_category: str = Query(None, description="Type of item", enum=["starter", "main course", "dessert", "drink"]),
    new_stock: int = None,
    availability: bool = Query(None, description="Is the item available ?", enum=[True, False]),
) -> dict:
    """If you want to edit an item (name, price, quantity etc.)."""
    try:
        item_service.update(name_item, new_name, new_price, new_category, new_stock, availability)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if new_name is None:
        item = item_repo.find_item_by_name(name_item)
    else:
        item = item_repo.find_item_by_name(new_name)
    return {
        "detail": "Item updated successfully",
        "name_item": item.name_item,
        "price": round(item.price / 100, 2),
        "category": item.category,
        "stock": item.stock,
        "availability": item.exposed,
    }


@administrator_router.delete("/Storage/Delete_Item", status_code=status.HTTP_200_OK)
def Delete_Item(name_item) -> str:
    """Function that calls the function to delete an item.

    Parameters
    -------
    name_item: str
        item's name

    Returns
    -------
    Item
        Returns the Item that has been deleted.
    """
    try:
        item_deleted = item_service.delete_item(name_item)
        return item_deleted
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@administrator_router.patch("/Edit_Profile", status_code=status.HTTP_200_OK)
def Edit_Profile(
    firstname: Optional[str] = Query(None, description="First name"),
    lastname: Optional[str] = Query(None, description="Last name"),
    password: Optional[str] = Query(None, description="Password"),
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())] = None,
) -> dict:
    """If you want to edit your own profile."""

    username = get_user_from_credentials(credentials).username

    try:
        user = user_service.update_user(username, firstname, lastname, password)
    except Exception as error:
        raise HTTPException(status_code=403, detail=f"Error updating profile: {error}") from error

    return {
        "detail": "Profile updated successfully",
        "firstname": user.firstname,
        "lastname": user.lastname,
    }
