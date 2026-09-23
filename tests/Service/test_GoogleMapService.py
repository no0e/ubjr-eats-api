import os

import pytest

from src.Service.GoogleMapService import GoogleMap

# These call Google for real and assert exact distances, so they need a key
# with billing attached and they move when Google changes a route. Skipped
# rather than deleted: when a key is present they are the only check that the
# request shape is still right.
pytestmark = pytest.mark.skipif(
    not os.environ.get("GOOGLE_MAPS_API_KEY"),
    reason="needs GOOGLE_MAPS_API_KEY; these tests hit the live Google API",
)

google_service = GoogleMap()


def test_geocoding_address():
    address = google_service.geocoding_address("51 rue Blaise Pascal, 35170 Bruz")
    assert round(address["lat"], 5) == 48.05089
    assert round(address["lng"], 5) == -1.74203
    with pytest.raises(Exception) as exception:
        google_service.geocoding_address("hdjdhfyej")
    assert str(exception.value) == "The address: hdjdhfyej is not found."


def test_get_directions():
    dest1 = google_service.geocoding_address("11 Avenue Robert Schuman, 35170 Bruz")
    dest2 = google_service.geocoding_address("6 Rue des Frères Mongolfier, 35170 Bruz")
    itinerary = google_service.get_directions([dest1, dest2], "driving")
    assert itinerary["distance_km"] == 1.57
    assert itinerary["duration_min"] == 4
    assert itinerary["stops"] == 1
    with pytest.raises(ValueError) as error:
        google_service.get_directions([], "driving")
    assert str(error.value) == "The destination list cannot be empty or null."
    with pytest.raises(ValueError) as error:
        google_service.get_directions(None, "driving")
    assert str(error.value) == "The destination list cannot be empty or null."


def test_generate_google_maps_link():
    restaurant = google_service.geocoding_address("51 rue Blaise Pascal, 35170 Bruz")
    dest1 = google_service.geocoding_address("11 Avenue Robert Schuman, 35170 Bruz")
    dest2 = google_service.geocoding_address("6 Rue des Frères Mongolfier, 35170 Bruz")
    link = google_service.generate_google_maps_link([dest1, dest2])
    strdest1 = str(dest1["lat"]) + "," + str(dest1["lng"])
    strdest2 = str(dest2["lat"]) + "," + str(dest2["lng"])
    strrest = str(restaurant["lat"]) + "," + str(restaurant["lng"])
    assert (
        link == f"https://www.google.com/maps/dir/?api=1&origin={strrest}&destination={strdest2}&waypoints={strdest1}"
    )
    with pytest.raises(ValueError) as error:
        google_service.get_directions([])
    assert str(error.value) == "The destination list cannot be empty or null."
    with pytest.raises(ValueError) as error:
        google_service.get_directions(None)
    assert str(error.value) == "The destination list cannot be empty or null."
