from typing import Optional

from src.DAO.DBConnector import DBConnector
from src.DAO.UserDAO import UserDAO
from src.Model.DeliveryDriver import DeliveryDriver


class DeliveryDriverDAO(UserDAO):
    """
    Data Access Object (DAO) for interacting with the 'deliverydrivers' table in the database.
    It inherits from UserDAO class.
    Provides methods to retrieve and insert user data.
    """

    def __init__(self, db_connector: DBConnector, test: bool = False):
        super().__init__(db_connector, test)

    def create(self, driver: DeliveryDriver) -> bool:
        """
        Function that create an instance of delivery driver in the deliverydrivers database.

        Parameters
        ----------
        driver : DeliveryDriver
            Model of DeliveryDriver which will be created


        Returns
        -------
        boolean
            Returns True if the delivery driver has been created, False otherwise.
        """
        if not isinstance(driver, DeliveryDriver):
            raise TypeError("The created driver must be of a type driver.")
        if self.get_by_username(driver.username) is None:
            raise ValueError(
                f"Username {driver.username} does not exist in users although it should to create a driver."
            )
        raw_created_driver = self.db_connector.sql_query(
            """
            INSERT INTO """
            + self.schema
            + """.delivery_drivers (username_delivery_driver, vehicle, is_available)
            VALUES (%(username_delivery_driver)s, %(vehicle)s, %(is_available)s)
            RETURNING *;
            """,
            {
                "username_delivery_driver": driver.username,
                "vehicle": driver.vehicle,
                "is_available": driver.is_available,
            },
            "one",
        )
        return raw_created_driver is not None

    def find_by_username(self, username: str) -> DeliveryDriver | None:
        """
        Function that find a delivery driver by their username.

        Parameters
        ----------
        username : str
            Username of the delivery driver we want to find


        Returns
        -------
        DeliveryDriver | None
            Returns a DeliveryDriver if found, None otherwise
        """
        query = (
            """
            SELECT d.username_delivery_driver as username, u.firstname, u.lastname, u.salt, u.account_type, u.password,
            d.vehicle, d.is_available
            FROM """
            + self.schema
            + """.delivery_drivers as d
            JOIN """
            + self.schema
            + """.users as u ON u.username = d.username_delivery_driver
            WHERE d.username_delivery_driver = %(username)s
        """
        )
        raw = self.db_connector.sql_query(query, {"username": username}, return_type="one")
        return DeliveryDriver(**raw) if raw else None

    def update_delivery_driver(
        self, username: str, vehicle: Optional[str] = None, is_available: Optional[bool] = None
    ) -> bool:
        """
        Function that update attributes of a delivery driver by their username.
        It could update any attributes among their vehicle and availability.

        Parameters
        ----------
        username : str
            Username of the customer we want to find
        vehicle : Optional[str] = None
            New vehicle, could be None if one wants to keep the previous one
        is_available : Optional[bool] = None
            New avaibility, could be None if one wants to keep the preivous one


        Returns
        -------
        bool
            Returns True if the update is done, False otherwise
        """
        current_driver = self.find_by_username(username)
        if not isinstance(current_driver, DeliveryDriver):
            return False

        vehicle = vehicle if vehicle is not None else current_driver.vehicle
        is_available = is_available if is_available is not None else current_driver.is_available

        set_clause = []
        params = {"username": username}

        if vehicle != current_driver.vehicle:
            set_clause.append("vehicle = %(vehicle)s")
            params["vehicle"] = vehicle

        if is_available != current_driver.is_available:
            set_clause.append("is_available = %(is_available)s")
            params["is_available"] = is_available

        if not set_clause:
            return False

        query = (
            """UPDATE """ + self.schema + f""".delivery_drivers
            SET {", ".join(set_clause)}"""
            f""" WHERE username_delivery_driver = %(username)s
        """
        )
        self.db_connector.sql_query(query, params, return_type=None)

        return True

    def delete(self, driver: DeliveryDriver) -> bool:
        """
        Function that delete a delivery driver.

        Parameters
        ----------
        driver : DeliveryDriver
            Driver we want to delete

        Returns
        -------
        boolean
            Returns True if the driver is deleted, False otherwise
        """
        if not isinstance(driver, DeliveryDriver):
            return False
        self.db_connector.sql_query(
            "DELETE FROM " + self.schema + ".delivery_drivers WHERE username_delivery_driver = %s",
            [driver.username],
        )
        return True

    def drivers_available(self) -> list[DeliveryDriver]:
        """
        Function that shows all available drivers.

        Returns
        -------
        list[DeliveryDriver]
            List of all available drivers
        """
        query = f"""
            SELECT username_delivery_driver, vehicle, is_available
            FROM {self.schema}.delivery_drivers
            WHERE is_available = TRUE
        """
        try:
            rows = self.db_connector.sql_query(query, return_type="all")
            # Map the query result keys to the DeliveryDriver constructor arguments
            return [self.find_by_username(r["username_delivery_driver"]) for r in rows]
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error fetching available drivers: {e}")
            return []
