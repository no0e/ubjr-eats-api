from typing import Optional

from src.DAO.AdministratorDAO import AdministratorDAO
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDAO import DeliveryDAO
from src.DAO.DeliveryDriverDAO import DeliveryDriverDAO
from src.DAO.OrderDAO import OrderDAO
from src.DAO.UserDAO import UserDAO
from src.Model.Administrator import Administrator
from src.Model.Customer import Customer
from src.Model.DeliveryDriver import DeliveryDriver
from src.Model.User import User
from src.Service.GoogleMapService import GoogleMap
from src.Service.PasswordService import check_password_strength, create_salt, hash_password

db_connector = DBConnector()
google_service = GoogleMap()
order_repo = OrderDAO(db_connector)
delivery_repo = DeliveryDAO(db_connector)


class UserService:
    """Class with all Service methods of a user."""

    def __init__(
        self,
        user_repo: UserDAO,
        admin_repo: AdministratorDAO,
        driver_repo: DeliveryDriverDAO,
        customer_repo: CustomerDAO,
    ):
        self.user_repo = user_repo
        self.admin_repo = admin_repo
        self.driver_repo = driver_repo
        self.customer_repo = customer_repo

    def create_user(
        self,
        username: str,
        firstname: str,
        lastname: str,
        password: str,
        address="51 rue Blaise Pascal, 35170 Bruz",
        account_type="Customer",
    ) -> User:
        """Function that creates a user from its attributes.

        Parameters
        ----------
        username : str
            user's username
        firstname : str
            user's firstname
        lastname : str
            user's lastname
        password : str
            user's password
        address : str
            user's address needed to create a customer account, by default "51 rue Blaise Pascal, 35170 Bruz"
        account_type : str
            user's account type, by default "Customer"


        Returns
        -------
        User
            Returns the user that has been created.
        """
        if self.username_exists(username):
            raise ValueError("Username already taken.")
        check_password_strength(password)
        salt = create_salt()
        new_password = hash_password(password, salt)
        self.user_repo.create_user(
            User(
                username=username,
                firstname=firstname,
                lastname=lastname,
                password=new_password,
                salt=salt,
                account_type=account_type,
            )
        )
        if account_type == "Administrator":
            self.admin_repo.create(
                Administrator(
                    username=username,
                    firstname=firstname,
                    lastname=lastname,
                    password=new_password,
                    salt=salt,
                    account_type=account_type,
                )
            )
        elif account_type == "DeliveryDriver":
            self.driver_repo.create(
                DeliveryDriver(
                    username=username,
                    firstname=firstname,
                    lastname=lastname,
                    password=new_password,
                    salt=salt,
                    account_type=account_type,
                    vehicle="driving",
                    is_available=False,
                )
            )
        else:
            self.customer_repo.create(
                Customer(
                    username=username,
                    firstname=firstname,
                    lastname=lastname,
                    password=new_password,
                    salt=salt,
                    account_type=account_type,
                    address=address,
                )
            )
            try:
                google_service.geocoding_address(address)
            except TypeError as e:
                self.delete_user(username)
                raise ValueError("Address not valid.") from e
        return User(
            username=username,
            firstname=firstname,
            lastname=lastname,
            password=new_password,
            salt=salt,
            account_type=account_type,
        )

    def get_user(self, user_username: str) -> User | None:
        """Function that gives a user by the username given.

        Parameters
        ----------
        user_username : str
            user's username to search

        Returns
        -------
        User
            Instance of the user with the assiociated username given.
        """
        return self.user_repo.get_by_username(user_username)

    def username_exists(self, username: str) -> bool:
        """Function that checks if a given username is already existing in the database.

        Parameters
        ----------
        username : str
            username to check

        Returns
        -------
        bool
            True if the username is already existing, False otherwise.
        """
        return self.user_repo.get_by_username(username) is not None

    def delete_user(self, username: str) -> bool:
        """Function that delete a user from our data given their username.

        Parameters
        ----------
        username : str
            username of the user we want to delete.

        Returns
        -------
        bool
            True if the deletion is done, False otherwise.
        """
        if self.get_user(username).account_type == "Administrator":
            self.admin_repo.delete(self.admin_repo.find_by_username(username))
        elif self.get_user(username).account_type == "DeliveryDriver":
            self.driver_repo.delete(self.driver_repo.find_by_username(username))
            if order_repo.find_order_by_driver(username) is not None:
                for order in order_repo.find_order_by_driver(username):
                    order_repo.delete(order)
            if delivery_repo.find_delivery_by_driver(username) is not None:
                for delivery in delivery_repo.find_delivery_by_driver(username):
                    delivery_repo.delete(delivery)
        else:
            self.customer_repo.delete(self.customer_repo.find_by_username(username))
            if order_repo.find_order_by_user(username) is not None:
                for order in order_repo.find_order_by_user(username):
                    order_repo.delete(order)
        return True if self.user_repo.delete_user(self.get_user(username)) else False

    def update_user(
        self,
        username: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        """Function that update the user's attributes.

        Parameters
        ----------
        username : str
            user's username
        firstname : str | None
            user's firstname
        lastname : str | None
            user's lastname
        password : str | None
            user's password

        Returns
        -------
        User
            Returns the user with updated information.
        """
        new_firstname: str
        new_lastname: str
        new_password: str
        user = self.user_repo.get_by_username(username)
        if firstname is None:
            new_firstname = user.firstname
        else:
            new_firstname = firstname
        if lastname is None:
            new_lastname = user.lastname
        else:
            new_lastname = lastname
        if password is None:
            new_password = user.password
        else:
            check_password_strength(password)
            salt = user.salt
            new_password = hash_password(password, salt)
        self.user_repo.update_user(username, new_firstname, new_lastname, new_password)
        return user
