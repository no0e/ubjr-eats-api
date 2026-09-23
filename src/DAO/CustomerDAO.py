from typing import Optional

from src.DAO.UserDAO import UserDAO
from src.Model.Customer import Customer
from src.Service.GoogleMapService import GoogleMap

google_service = GoogleMap()


class CustomerDAO(UserDAO):
    """
    Data Access Object (DAO) for interacting with the 'customers' table in the database.
    It inherits from UserDAO class.
    Provides methods to retrieve and insert user data.
    """

    def __init__(self, db_connector, test: bool = False):
        super().__init__(db_connector, test)

    def create(self, customer: Customer) -> bool:
        """
        Function that create an instance of customer in the customers database.

        Parameters
        ----------
        customer : Customer
            Model of customer which will be created


        Returns
        -------
        boolean
            Returns True if the customer has been created, False otherwise.
        """
        if not isinstance(customer, Customer):
            raise TypeError("The created customer should be type of Customer.")
        raw_created_customer = self.db_connector.sql_query(
            """
            INSERT INTO """
            + self.schema
            + """.customers (username_customer, address)
            VALUES (%(username_customer)s, %(address)s)
            RETURNING *;
            """,
            {"username_customer": customer.username, "address": customer.address},
            "one",
        )
        return raw_created_customer is not None

    def find_by_username(self, username: str) -> Customer | None:
        """
        Function that find an customer by their username.

        Parameters
        ----------
        username : str
            Username of the customer we want to find


        Returns
        -------
        Customer | None
            Returns an Customer if found, None otherwise
        """
        if not isinstance(username, str):
            raise TypeError("Username should be a string.")
        query = (
            """
            SELECT c.username_customer as username, u.firstname, u.lastname, u.salt, u.account_type, u.password,
            c.address
            FROM """
            + self.schema
            + """.customers as c
            JOIN """
            + self.schema
            + """.users as u ON u.username = c.username_customer
            WHERE username = %s;
        """
        )
        raw = self.db_connector.sql_query(query, [username], return_type="one")
        return Customer(**raw) if raw else None

    def update_customer(self, username: str, address: Optional[str] = None) -> bool:
        """
        Update an existing customer's address.

        Parameters
        ---
        username: str
            customer's username
        address: str
            new customer's address we want to set in the database

        Return
        ---
        bool
            Returns True if the update succeed, False otherwise.
        """
        current_customer = self.find_by_username(username)
        if current_customer is None:
            raise ValueError(f"Customer with username '{username}' not found.")
        if address is None:
            address = current_customer.address
        else:
            google_service.geocoding_address(address)

        set_clause = []
        params = {"username": username}

        if address != current_customer.address:
            set_clause.append("address = %(address)s")
            params["address"] = address

        if not set_clause:
            return False

        query = (
            """UPDATE """
            + self.schema
            + """.customers
            SET {", ".join(set_clause)}
            WHERE username_customer = %(username)s
        """
        )
        self.db_connector.sql_query(query, params, return_type=None)

        return True

    def delete(self, customer: Customer) -> bool:
        """
        Function that delete a customer.

        Parameters
        ----------
        customer : Customer
            Customer we want to delete

        Returns
        -------
        boolean
            Returns True if the customer is deleted, False otherwise
        """
        if not isinstance(customer, Customer):
            raise TypeError(f"{customer} should be type of Customer.")
        if self.find_by_username(customer.username) is None:
            raise ValueError(f"{customer.username} doesn't exist.")
        self.db_connector.sql_query(
            "DELETE FROM " + self.schema + ".customers WHERE username_customer = %s",
            [customer.username],
        )
        return True
