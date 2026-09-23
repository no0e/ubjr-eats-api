from typing import List, Optional

import pytest

from src.Model.Delivery import Delivery
from src.Service.DeliveryService import DeliveryService


class MockDeliveryRepo:
    def __init__(self):
        self.deliveries = {}
        self.auto_id = 1

    def create(self, delivery: Delivery) -> bool:
        if not isinstance(delivery, Delivery):
            raise TypeError(f"The type of {delivery} should be Delivery.")

        new_id = self.auto_id
        self.auto_id += 1

        delivery.id_delivery = new_id

        self.deliveries[new_id] = delivery

        return delivery

    def find_by_username(self, username: str) -> Optional[Delivery]:
        return self.deliveries.get(username)

    def get_available_deliveries(self) -> List[Delivery]:
        return [delivery for delivery in self.deliveries.values() if delivery.is_accepted is False]

    def get_by_id(self, id_delivery) -> Delivery:
        return self.deliveries.get(id_delivery)


    def set_delivery_accepted(self, id_delivery: int, username_delivery_driver: str):
        if id_delivery == 4:
            return False

        delivery = self.deliveries.get(id_delivery)
        delivery.is_accepted = True
        delivery.username_delivery_driver = username_delivery_driver

        last_order_id = delivery.id_orders[-1]

        if str(last_order_id) not in self.orders:
            self.orders[str(last_order_id)] = {"id_order": last_order_id}

        self.orders[str(last_order_id)]["username_delivery_driver"] = username_delivery_driver

        return True


class MockGoogleMap:
    """Mock to simulate the Google Maps API."""

    def geocoding_address(self, address: str) -> dict:
        """Simulate the convertion of an address into GPS coordonates."""
        if "Paris" in address:
            return {"lat": 48.8566, "lng": 2.3522}
        if "Lyon" in address:
            return {"lat": 45.7640, "lng": 4.8357}
        if "Unknown address" in address:
            raise TypeError("The address is unfoundable")
        return {"lat": 0.0, "lng": 0.0}

    def get_directions(self, destinations: List[dict], mode: str) -> dict:
        """Simulate the calculation of an itinary and a duration."""
        duration = 15 + (len(destinations) * 15)
        distance = len(destinations) * 10

        return {"duration_min": duration, "distance_km": distance}

    def generate_google_maps_link(self, destination_coords: List[dict]) -> str:
        """Simulate the creation of a Google Maps link."""
        lat = destination_coords[0]["lat"]
        lng = destination_coords[0]["lng"]
        return f"https://mock.google.com/maps?q={lat},{lng}"


@pytest.fixture
def delivery_repo():
    repo = MockDeliveryRepo()

    repo.deliveries = {
        1: repo.create(
            Delivery(
                id_delivery=1,
                username_delivery_driver="ernesto",
                duration="50",
                id_orders=[1, 2],
                stops=["13 Main St.", "4 Salty Spring Av."],
                is_accepted=True,
            )
        ),
        2: repo.create(
            Delivery(
                id_delivery=2,
                username_delivery_driver="ernesto1",
                duration="15",
                id_orders=[1],
                stops=["13 Main St."],
                is_accepted=False,
            )
        ),
        3: repo.create(
            Delivery(
                id_delivery=3,
                username_delivery_driver="driver_test",
                duration="10",
                id_orders=[3],
                stops=[],
                is_accepted=True,
            )
        ),
        4: repo.create(
            Delivery(
                id_delivery=4,
                username_delivery_driver=None,
                duration="10",
                id_orders=[3],
                stops=["Paris"],
                is_accepted=False,
            )
        ),
        5: repo.create(
            Delivery(
                id_delivery=5,
                username_delivery_driver=None,
                duration="10",
                id_orders=[3],
                stops=["Paris"],
                is_accepted=False,
            )
        ),
    }
    return repo


@pytest.fixture
def googlemap():
    return MockGoogleMap()


@pytest.fixture
def delivery_service(delivery_repo, googlemap):
    return DeliveryService(delivery_repo, googlemap)


def test_create_success(delivery_service):
    delivery = delivery_service.create([1, 2], ["13 Main St.", "4 Salty Spring Av."])
    assert delivery.id_orders == [1, 2]
    assert delivery.stops == ["13 Main St.", "4 Salty Spring Av."]
    assert delivery.id_delivery == 6


def test_create_failure(delivery_service, delivery_repo):
    original_create = delivery_repo.create

    def failing_create(delivery: Delivery):
        return False

    delivery_repo.create = failing_create

    with pytest.raises(ValueError, match="Failed to create delivery in the database."):
        delivery_service.create([10, 11], ["Test St."])
    delivery_repo.create = original_create


def test_get_available_deliveries_success(delivery_service):
    deliveries = delivery_service.get_available_deliveries("driving")
    assert len(deliveries) == 3
    delivery1 = deliveries[0]
    assert delivery1["username_delivery_driver"] == "ernesto1"
    assert delivery1["duration"] == 15
    assert delivery1["id_orders"] == [1]
    assert delivery1["stops"] == ["13 Main St."]


def test_accept_delivery_success(delivery_service):
    message = delivery_service.accept_delivery(4, "ernesto", "driving")
    assert message == {
        "message": "Delivery accepted successfully",
        "delivery_id": 4,
        "duration": 30,
        "google_maps_link": "https://mock.google.com/maps?q=48.8566,2.3522",
    }


def test_accept_delivery_failed(delivery_service):
    with pytest.raises(ValueError) as error_id:
        delivery_service.accept_delivery(6, "driver_no_stops", "driving")
    assert str(error_id.value) == "Delivery not found"
    with pytest.raises(ValueError) as error_id_not:
        delivery_service.accept_delivery(1, "driver_no_stops", "driving")
    assert str(error_id_not.value) == "Delivery already accepted"


def test_accept_delivery_already_accepted(delivery_service):
    with pytest.raises(ValueError) as error_driver:
        delivery_service.accept_delivery(1, "driver", "driving")
    assert str(error_driver.value) == "Delivery already accepted"


def test_accept_delivery_unfoundable_address(delivery_service, delivery_repo):
    new_delivery = Delivery(
        username_delivery_driver=None,
        duration="20",
        id_orders=[6],
        stops=["Unknown address"],
        is_accepted=False,
        id_delivery=8,
    )
    id_delivery = delivery_repo.create(new_delivery).id_delivery
    with pytest.raises(TypeError, match="The address is unfoundable"):
        delivery_service.accept_delivery(id_delivery, "driver_fail", "driving")
