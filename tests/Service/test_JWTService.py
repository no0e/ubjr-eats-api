import datetime

import jwt
from freezegun import freeze_time
from jwt.exceptions import ExpiredSignatureError
from pytest import raises

from src.Service.JWTService import JwtService

jwt_service = JwtService("mysecret")


@freeze_time("2024-08-26 12:00:00")
def test_encode_jwt():
    username = "Noé"
    account_type = "customer"

    jwtResponse = jwt_service.encode_jwt(username=username, account_type=account_type)

    expected_payload = {
        "username": "Noé",
        "account_type": "customer",
        "expiry_timestamp": 1724674200.0,
    }

    decoded = jwt.decode(jwtResponse.access_token, "mysecret", algorithms=["HS256"])
    assert decoded == expected_payload


@freeze_time("2024-08-26 12:00:00")
def test_decode_jwt():
    payload = {
        "username": "Noé",
        "account_type": "customer",
        "expiry_timestamp": 1724674200.0,
    }

    token = jwt.encode(payload, "mysecret", algorithm="HS256")

    decoded_jwt = jwt_service.decode_jwt(token)

    assert decoded_jwt["username"] == "Noé"
    assert decoded_jwt["account_type"] == "customer"
    assert datetime.datetime.fromtimestamp(decoded_jwt["expiry_timestamp"]) == datetime.datetime(2024, 8, 26, 12, 10, 0)


@freeze_time("2024-08-26 12:00:00")
def test_validate_user_jwt_valid():
    payload = {
        "username": "Noé",
        "account_type": "customer",
        "expiry_timestamp": 1724674200.0,
    }

    token = jwt.encode(payload, "mysecret", algorithm="HS256")

    decoded = jwt_service.validate_user_jwt(token)
    assert decoded == payload


@freeze_time("2024-08-26 12:11:00")
def test_validate_user_jwt_expired():
    payload = {
        "username": "Noé",
        "account_type": "customer",
        "expiry_timestamp": 1724674200.0,
    }

    token = jwt.encode(payload, "mysecret", algorithm="HS256")

    with raises(ExpiredSignatureError):
        jwt_service.validate_user_jwt(token)
