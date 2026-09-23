from typing import List, Optional

import pytest

from src.Model.Delivery import Delivery
from src.Model.DeliveryDriver import DeliveryDriver
from src.Model.Order import Order
from src.Service.DeliveryDriverService import DeliveryDriverService


class MockDriverRepo:
    def __init__(self):
        self.drivers = {}
        self.orders = {}

    def create(self, driver):
        self.drivers[driver.username] = driver

    def find_by_username(self, username: str) -> Optional[DeliveryDriver]:
        return self.drivers.get(username)


class MockDeliveryRepo:
    def __init__(self):
        self.deliveries = {}

    def find_by_username(self, username: str) -> Optional[Delivery]:
        return self.deliveries.get(username)

    def get_available_deliveries(self) -> List[Delivery]:
        return [delivery for delivery in self.deliveries.values() if delivery.is_accepted is False]

    def set_delivery_accepted(self, id_delivery: int, username_delivery_driver: str):
        if id_delivery == 4:
            return False

        delivery = self.deliveries.get(id_delivery)

        if not delivery:
            raise ValueError("Delivery not found")

        if not delivery.id_orders:
            raise ValueError("Orders not found for delivery")

        delivery.is_accepted = True
        delivery.username_delivery_driver = username_delivery_driver
        delivery = self.deliveries.get(id_delivery)

        if not delivery:
            raise ValueError("Delivery not found")

        if not delivery.id_orders:
            raise ValueError("Orders not found for delivery")

        delivery.is_accepted = True
        delivery.username_delivery_driver = username_delivery_driver

        last_order_id = delivery.id_orders[-1]
        if str(last_order_id) not in self.orders:
            self.orders[str(last_order_id)] = {"id_order": last_order_id}

        self.orders[str(last_order_id)]["username_delivery_driver"] = username_delivery_driver

        
        destinations = [
            {
                "lat": 48.117266,
                "lng": -1.6777926,
                "address": stop,
            }
            for stop in delivery.stops
        ]

        return delivery, destinations

    def accept_delivery(self, delivery_id: int, driver_username: str) -> dict:
        deliveries = self.delivery_repo.get_available_deliveries()
        delivery = next((d for d in deliveries if d.id_delivery == delivery_id), None)
        if not delivery:
            raise ValueError("Delivery not available or already accepted")

        success = self.delivery_repo.set_delivery_accepted(delivery_id, driver_username)
        if not success:
            raise ValueError("Delivery could not be accepted")

        if delivery.stops:
            destinations_for_map = delivery.stops
        else:
            destinations_for_map = [{"lat": 48.050245, "lng": -1.741515}]

        link = self.google_service.generate_google_maps_link(destinations_for_map)

        return {"delivery_id": delivery_id, "google_maps_link": link}


class MockGoogleRepo:
    def __init__(self):
        self.restaurant_coords = {"lat": 48.111339, "lng": -1.68002}

    def generate_google_maps_link(self, destinations):
        if not destinations:
            raise ValueError("The list of destinations cannot be empty")

        origin = f"{self.restaurant_coords['lat']},{self.restaurant_coords['lng']}"

        destination = ""
        waypoints = ""

        if isinstance(destinations, list) and all(isinstance(d, str) for d in destinations):
            destination = destinations[-1]
            waypoints = "|".join(destinations[:-1])

        elif isinstance(destinations, list) and isinstance(destinations[0], dict):
            if "address" in destinations[0]:
                destination = destinations[-1]["address"]
                waypoints = "|".join(d["address"] for d in destinations[:-1])

            else:
                destination = f"{destinations[-1]['lat']},{destinations[-1]['lng']}"
                waypoints = "|".join(f"{d['lat']},{d['lng']}" for d in destinations[:-1])

        elif isinstance(destinations, dict):
            destination = f"{destinations['lat']},{destinations['lng']}"
            waypoints = ""
        else:
            raise TypeError("Destinations format is not recognized by the mock.")

        return (
            "http://googleusercontent.com/maps.google.com/?"
            f"origin={origin}"
            f"&destination={destination}"
            f"&waypoints={waypoints}"
        )


@pytest.fixture
def driver_repo():
    repo = MockDriverRepo()

    repo.drivers = {
        "ernesto": DeliveryDriver(
            username="ernesto",
            firstname="Ernest",
            lastname="Eagle",
            password="364a9f83d2ab94505ba9baecd0fe59c88b082f982e8d8cf8070171bae171fcbe",
            salt="no",
            account_type="DeliveryDriver",
            vehicle="car",
            is_available=False,
        ),
        "ernesto1": DeliveryDriver(
            username="ernesto1",
            firstname="Ernest",
            lastname="Eagle",
            salt="no",
            account_type="DeliveryDriver",
            password="364a9f83d2ab94505ba9baecd0fe59c88b082f982e8d8cf8070171bae171fcbe",
            vehicle="foot",
            is_available=True,
        ),
    }

    return repo


@pytest.fixture
def delivery_repo():
    repo = MockDeliveryRepo()

    repo.deliveries = {
        1: Delivery(
            id_delivery=1,
            username_delivery_driver="ernesto",
            duration="50",
            id_orders=[1, 2],
            stops=["13 Main St.", "4 Salty Spring Av."],
            is_accepted=True,
        ),
        2: Delivery(
            id_delivery=2,
            username_delivery_driver="ernesto1",
            duration="15",
            id_orders=[1],
            stops=["13 Main St."],
            is_accepted=False,
        ),
        3: Delivery(
            id_delivery=3,
            username_delivery_driver="driver_test",
            duration="10",
            id_orders=[3],
            stops=[],
            is_accepted=False,
        ),
        4: Delivery(
            id_delivery=4,
            username_delivery_driver=None,
            duration="10",
            id_orders=[3],
            stops=["10 Failed St."],
            is_accepted=False,
        ),
    }
    repo.orders = {
        1: Order(
            id_order=None,
            username_customer="bobbia",
            username_delivery_driver="ernesto1",
            address="13 Main St.",
            items={"galette saucisse": 2, "cola": 1},
        ),
        2: Order(
            id_order=None,
            username_customer="bobbia",
            username_delivery_driver="ernesto",
            address="13 Main St.",
            items={"galette saucisse": 39},
        ),
    }

    return repo


@pytest.fixture
def google_repo():
    return MockGoogleRepo()


@pytest.fixture
def deliverydriver_service(driver_repo, delivery_repo, google_repo):
    return DeliveryDriverService(driver_repo=driver_repo, delivery_repo=delivery_repo, google_service=google_repo)


def test_get_driver_success(deliverydriver_service):
    driver = deliverydriver_service.get_driver("ernesto")
    assert driver.username == "ernesto"
    assert driver.vehicle == "car"
    assert driver.firstname == "Ernest"
    assert driver.lastname == "Eagle"
    assert driver.password == "364a9f83d2ab94505ba9baecd0fe59c88b082f982e8d8cf8070171bae171fcbe"
    assert driver.salt == "no"
    assert driver.account_type == "DeliveryDriver"
    assert driver.is_available is False


def test_get_driver_not_found(deliverydriver_service):
    driver = deliverydriver_service.get_driver("non_existent_driver")
    assert driver is None


def test_get_available_deliveries_success(deliverydriver_service):
    deliveries = deliverydriver_service.get_available_deliveries()
    assert len(deliveries) == 3

    d = deliveries[0]

    assert d.id_delivery == 2
    assert d.username_delivery_driver == "ernesto1"
    assert d.duration == 15
    assert d.id_orders == [1]
    assert d.stops == ["13 Main St."]
    assert d.is_accepted is False


def test_accept_delivery_success(deliverydriver_service):
    delivery = deliverydriver_service.accept_delivery(2, "ernesto1")
    expected_link = (
        "http://googleusercontent.com/maps.google.com/?origin=48.111339,-1.68002&destination=13 Main St.&waypoints="
    )
    assert delivery == {"delivery_id": 2, "google_maps_link": expected_link}


def test_accept_delivery_failed(deliverydriver_service):
    with pytest.raises(ValueError) as error_delivery:
        deliverydriver_service.accept_delivery(1, "ernesto")
    assert str(error_delivery.value) == "Delivery not available or already accepted"


def test_accept_delivery_with_no_stops(deliverydriver_service):
    delivery = deliverydriver_service.accept_delivery(3, "ernesto1")

    expected_link = (
        "http://googleusercontent.com/maps.google.com/?"
        "origin=48.111339,-1.68002"
        "&destination=48.050245,-1.741515"
        "&waypoints="
    )
    assert delivery == {"delivery_id": 3, "google_maps_link": expected_link}


def test_accept_delivery_failed_repo_update(deliverydriver_service):
    with pytest.raises(ValueError) as error:
        deliverydriver_service.accept_delivery(4, "ernesto1")
    assert str(error.value) == "Delivery could not be accepted"
