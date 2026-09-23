from dotenv import load_dotenv

from src.DAO.AdministratorDAO import AdministratorDAO
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDAO import DeliveryDAO
from src.DAO.DeliveryDriverDAO import DeliveryDriverDAO
from src.DAO.ItemDAO import ItemDAO
from src.DAO.OrderDAO import OrderDAO
from src.DAO.UserDAO import UserDAO
from src.Service.AdministratorService import AdministratorService
from src.Service.CustomerService import CustomerService
from src.Service.DeliveryDriverService import DeliveryDriverService
from src.Service.DeliveryService import DeliveryService
from src.Service.GoogleMapService import GoogleMap
from src.Service.ItemService import ItemService
from src.Service.JWTService import JwtService
from src.Service.UserService import UserService

load_dotenv()
db_connector = DBConnector()
user_repo = UserDAO(db_connector)
admin_repo = AdministratorDAO(db_connector)
driver_repo = DeliveryDriverDAO(db_connector)
customer_repo = CustomerDAO(db_connector)
delivery_repo = DeliveryDAO(db_connector)
item_repo = ItemDAO(db_connector)


google_map_service = GoogleMap()
jwt_service = JwtService()
user_service = UserService(user_repo, admin_repo, driver_repo, customer_repo)
admin_service = AdministratorService(user_repo, admin_repo, driver_repo, customer_repo)
customer_service = CustomerService(ItemDAO, DeliveryDAO, CustomerDAO, OrderDAO, DeliveryDAO, DeliveryService)
driver_service = DeliveryDriverService(driver_repo, delivery_repo, google_map_service)
item_service = ItemService(item_repo)
