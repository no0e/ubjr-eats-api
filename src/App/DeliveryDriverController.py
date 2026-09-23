from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials

from src.App.Auth_utils import get_user_from_credentials, require_account_type
from src.App.JWTBearer import JWTBearer
from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDAO import DeliveryDAO
from src.DAO.DeliveryDriverDAO import DeliveryDriverDAO
from src.DAO.UserDAO import UserDAO
from src.Service.DeliveryDriverService import DeliveryDriverService
from src.Service.DeliveryService import DeliveryService
from src.Service.GoogleMapService import GoogleMap

from .init_app import user_service

# Instanciation du connecteur et des DAOs
db_connector = DBConnector()
delivery_dao = DeliveryDAO(db_connector)
driver_dao = DeliveryDriverDAO(db_connector)
user_dao = UserDAO(db_connector)

# Services instanciés avec les bons DAOs
google_service = GoogleMap()
delivery_service = DeliveryService(delivery_dao, google_service)
driver_service = DeliveryDriverService(driver_dao, delivery_dao, user_dao)

deliverydriver_router = APIRouter(
    prefix="/delivery_driver", tags=["DeliveryDriver"], dependencies=[Depends(require_account_type("DeliveryDriver"))]
)


@deliverydriver_router.get("/Delivery", status_code=status.HTTP_200_OK)
def view_available_deliveries(credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]) -> dict:
    """If you want to see all available deliveries."""
    username_driver = get_user_from_credentials(credentials).username
    vehicle_driver = driver_dao.find_by_username(username_driver).vehicle
    deliveries = delivery_service.get_available_deliveries(vehicle_driver)
    return {"available_deliveries": deliveries}


@deliverydriver_router.post(
    "/Delivery/Accept/{id_delivery}", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())]
)
def accept_delivery(
    id_delivery: int,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())],
) -> dict:
    """If you want to accept a delivery by typing its id."""
    username_driver = get_user_from_credentials(credentials).username
    vehicle_driver = driver_dao.find_by_username(username_driver).vehicle
    try:
        return delivery_service.accept_delivery(id_delivery, username_driver, vehicle_driver)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@deliverydriver_router.patch("/Edit_Profile", status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
def edit_profile(
    firstname: Optional[str] = Query(None, description="First name"),
    lastname: Optional[str] = Query(None, description="Last name"),
    password: Optional[str] = Query(None, description="Password"),
    vehicle: Optional[str] = Query(None, description="Type of vehicle", enum=["driving", "walking", "bicycling"]),
    is_available: Optional[bool] = Query(None, description="Driver availability"),
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())] = None,
) -> dict:
    """If you want to update your own profile."""

    username = get_user_from_credentials(credentials).username
    try:
        driver = driver_dao.update_delivery_driver(username, vehicle, is_available)
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
        "vehicle": driver.vehicle,
        "is_available": driver.is_available,
    }
