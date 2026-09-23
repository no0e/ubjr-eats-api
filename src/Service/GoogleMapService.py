import os

import requests
from dotenv import load_dotenv

load_dotenv()


def _api_key() -> str:
    """The Google Maps key, read from the environment at call time.

    Read here rather than at import so the module can be imported, and the
    rest of the application tested, on a machine that has no key. The earlier
    version of this file carried the key as a literal, which is how it ended
    up in a public git history.
    """
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not key:
        raise RuntimeError(
            "GOOGLE_MAPS_API_KEY is not set. Copy .env.sample to .env and put "
            "your own key in it; see the README for which APIs it needs."
        )
    return key


class GoogleMap:
    def __init__(self, restaurant_location="51 rue Blaise Pascal, 35170 Bruz"):
        self.restaurant_location = restaurant_location
        self.restaurant_coords = {"lat": 48.05089, "lng": -1.74203}

    def geocoding_address(self, address: str) -> dict:
        """Function that transforms an address into its GPS coordinates.

        Parameters
        ----------
        address: str
            the address written as a str

        Returns
        -------
        dict
            Dict containing the latitude and longitude values for the address.
        """
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": _api_key()}
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] != "OK":
            if data["status"] == "ZERO_RESULTS":
                raise TypeError(f"The address: {address} is not found.")
            else:
                raise Exception(f"Geocoding Error: {data['status']}")

        location = data["results"][0]["geometry"]["location"]
        return {"lat": round(location["lat"], 5), "lng": round(location["lng"], 5)}

    def get_directions(self, destinations: list[dict], mode: str = "driving") -> dict:
        """Function that computes the distance and duration for a itinerary.

        Parameters
        ----------
        destinations: list[dict]
            GPS coordinates under [{"lat": 48.0, "lng": -1.7}, {...}, ...] form.
            The last element being the final destination.
        mode: str
            driver's way of delivering: "driving", "bicycling" ou "walking".

        Returns
        -------
        dict
            Dict containing the total distance and duration of the itinerary.
        """
        if not destinations or len(destinations) == 0:
            raise ValueError("The destination list cannot be empty or null.")

        origin = f"{self.restaurant_coords['lat']},{self.restaurant_coords['lng']}"
        destination = f"{destinations[-1]['lat']},{destinations[-1]['lng']}"
        waypoints = "|".join(f"{wp['lat']},{wp['lng']}" for wp in destinations[:-1])

        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "waypoints": waypoints,
            "mode": mode,
            "key": _api_key(),
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] != "OK":
            if data["status"] == "ZERO_RESULTS":
                raise Exception("No itinerary found.")
            else:
                raise Exception(f"Directions Error: {data['status']}")

        legs = data["routes"][0]["legs"]
        total_distance = sum(leg["distance"]["value"] for leg in legs) / 1000  # km
        total_duration = sum(leg["duration"]["value"] for leg in legs) / 60  # minutes

        return {
            "distance_km": round(total_distance, 2),
            "duration_min": round(total_duration, 2),
            "mode": mode,
            "stops": len(destinations) - 1,
        }

    def generate_google_maps_link(self, destinations: list[dict]) -> str:
        """Function that generate a link associated with the delivery itinerary.

        Parameters
        ----------
        destinations: list[dict]
            GPS coordinates under [{"lat": 48.0, "lng": -1.7}, {...}, ...] form.
            The last element being the final destination.

        Returns
        -------
        str
            String of the link for the delivery.
        """
        if not destinations or len(destinations) == 0:
            raise ValueError("The destination list cannot be empty or null.")

        origin = f"{self.restaurant_coords['lat']},{self.restaurant_coords['lng']}"
        destination = f"{destinations[-1]['lat']},{destinations[-1]['lng']}"
        waypoints = "|".join(f"{wp['lat']},{wp['lng']}" for wp in destinations[:-1])

        return f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&waypoints={waypoints}"
