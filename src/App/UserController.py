from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Model.APIUser import APIUser
from src.Model.JWTResponse import JWTResponse
from src.Service.PasswordService import check_password_strength, validate_username_password

from .Auth_utils import get_user_from_credentials
from .init_app import jwt_service, user_repo, user_service
from .JWTBearer import JWTBearer

if TYPE_CHECKING:
    from src.Model.User import User

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(username: str, password: str, firstname: str, lastname: str, address: str) -> APIUser:
    """If you want to create a customer's account.
    Please note that you have to write your full postal address in the field indicated."""
    try:
        check_password_strength(password=password)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Password too weak") from e
    try:
        user: User = user_service.create_user(
            username=username.lower(), password=password, firstname=firstname, lastname=lastname, address=address
        )
    except Exception as error:
        raise HTTPException(status_code=409, detail=f"{error}") from error
    return APIUser(username=user.username.lower(), account_type="Customer")


@user_router.post("/jwt", status_code=status.HTTP_201_CREATED)
def login(username: str, password: str) -> JWTResponse:
    """If you want to log in to the application with your username and password.
    You have to copy and paste the token given below in the "authorize" box at the top right of the application.
    """
    try:
        user = validate_username_password(username=username.lower(), password=password, user_repo=user_repo)
    except Exception as error:
        raise HTTPException(status_code=403, detail=f"{error}") from error

    return jwt_service.encode_jwt(user.username.lower(), user.account_type)


@user_router.get("/me", dependencies=[Depends(JWTBearer())])
def get_user_own_profile(credentials: Annotated[HTTPAuthorizationCredentials, Depends(JWTBearer())]) -> APIUser:
    """If you want to check your username and type of account."""
    return get_user_from_credentials(credentials)
