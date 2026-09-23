from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.App.JWTBearer import JWTBearer
from src.Model.APIUser import APIUser

from .init_app import jwt_service, user_repo

_dependency = Depends(JWTBearer())


def get_user_from_credentials(credentials: HTTPAuthorizationCredentials) -> APIUser:
    """Function that returns a user given their credentials.

    Parameters
    ----------
    credentials: HTTPAuthorizationCredentials
        user's credentials

    Returns
    -------
    APIUser
        Returns the APIUser associated.
    """
    token = credentials.credentials
    try:
        payload = jwt_service.decode_jwt(token)
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Invalid token: {e}") from e

    username = payload.get("username")
    account_type = payload.get("account_type")
    if not username or not account_type:
        raise HTTPException(status_code=403, detail="Token missing required information")

    user = user_repo.get_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return APIUser(username=user.username, account_type=user.account_type)


def require_account_type(required_account_type: Literal["Administrator", "DeliveryDriver", "Customer"]):
    """This function returns a dependency that ensures the authenticated user has the required account type.

    Parameters
    ----------
    required_account_type: str
        The account type required to access the endpoint.

    Returns
    -------
    Callable
        A FastAPI dependency function that validates the authenticated user's role
        and returns the decoded JWT payload if authorised.
    """

    def wrapper(credentials: HTTPAuthorizationCredentials = _dependency):
        payload = jwt_service.decode_jwt(credentials.credentials)
        user_account_type = payload.get("account_type")
        if user_account_type != required_account_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied for role '{user_account_type}'"
            )
        return payload

    return wrapper
