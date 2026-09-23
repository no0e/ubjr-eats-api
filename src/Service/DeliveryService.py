from typing import List

from src.DAO.DeliveryDAO import DeliveryDAO
from src.Model.Delivery import Delivery
from src.Service.GoogleMapService import GoogleMap


class DeliveryService:
    """Service métier pour la gestion des livraisons."""

    def __init__(self, delivery_repo: DeliveryDAO, google_maps: GoogleMap):
        self.delivery_repo = delivery_repo
        self.googlemap = google_maps

    def create(self, id_orders: List[int], stops: List[str]) -> Delivery:
        """Function that creates a new delivery

        Parameters
        ----------
        id_orders: List[int]
            id's of the orders contained in the delivery
        stops: List[str]
            addresses associated with each order

        Returns
        -------
        Delivery
            The delivery that has been created
        """
        delivery = Delivery(id_orders=id_orders, stops=stops, is_accepted=False)
        success = self.delivery_repo.create(delivery)
        if not success:
            raise ValueError("Failed to create delivery in the database.")
        return delivery

    def get_available_deliveries(self, vehicule) -> dict:
        deliveries = self.delivery_repo.get_available_deliveries()

        enriched = []
        for d in deliveries:
            base = d.__dict__.copy()

            # adress -> GPS
            coords = [self.googlemap.geocoding_address(addr) for addr in d.stops]

            # any coords ?
            if not coords:
                continue

            route = self.googlemap.get_directions(destinations=coords, mode=vehicule)

            base["duration_min"] = route["duration_min"]
            base["distance_km"] = route["distance_km"]

            enriched.append(base)

        return enriched

    def accept_delivery(self, id_delivery: int, username_driver: str, vehicle: str) -> dict:
        """Function that allows a driver to accept a delivery, updates the database and provides a googlemap link.

        Parameters
        ----------
        id_delivery: int
            id of the concerned delivery.
        username_driver: str
            username of the concerned delivery driver.
        vehicle: str
            way of delivering of that same delivery driver.

        Returns
        -------
        dict
            Message that confirms the delivery acceptation and provides the googlemap link for the driver.
        """
        delivery = self.delivery_repo.get_by_id(id_delivery)
        if not delivery:
            raise ValueError("Delivery not found")
        if delivery.is_accepted:
            raise ValueError("Delivery already accepted")

        dests: List[dict] = [self.googlemap.geocoding_address(stop) for stop in delivery.stops]
        duration = self.googlemap.get_directions(destinations=dests, mode=vehicle)["duration_min"]
        self.delivery_repo.set_delivery_accepted(id_delivery, username_driver)

        if not isinstance(delivery.stops, list):
            raise ValueError("Stops are not under a list format.")
        if not delivery.stops or len(delivery.stops) == 0:
            raise ValueError("No delivery stops found")

        destination_address = delivery.stops[-1]
        destination_coords = [self.googlemap.geocoding_address(destination_address)]
        google_maps_link = self.googlemap.generate_google_maps_link(destination_coords)

        return {
            "message": "Delivery accepted successfully",
            "delivery_id": id_delivery,
            "duration": duration,
            "google_maps_link": google_maps_link,
        }
