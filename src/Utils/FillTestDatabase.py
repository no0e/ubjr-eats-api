import argparse
import json
import random

from faker import Faker

from src.DAO.DBConnector import DBConnector
from src.Service.PasswordService import create_salt, hash_password

fake = Faker()


def insert_auto(db, schema, table, data_dict):
    cols = list(data_dict.keys())
    vals = list(data_dict.values())
    col_str = ",".join(cols)
    placeholders = ",".join(["%s"] * len(cols))

    sql = f"""
        INSERT INTO {schema}.{table} ({col_str})
        VALUES ({placeholders})
        RETURNING *
    """
    return db.sql_query(sql, vals, return_type="one")


def populate_db(n_admins, n_drivers, n_customers, n_items, n_orders, n_deliveries, database):
    if not database.isidentifier():
        raise ValueError("Invalid schema/database name")

    db = DBConnector()

    print("=== Starting population ===")

    # ---------------- USERS ----------------
    def insert_user(account_type):
        username = fake.unique.user_name()
        raw_pw = fake.password()
        salt = create_salt()
        hashed_pw = hash_password(raw_pw, salt)

        insert_auto(
            db,
            database,
            "users",
            {
                "username": username,
                "firstname": fake.first_name(),
                "lastname": fake.last_name(),
                "password": hashed_pw,
                "salt": salt,
                "account_type": account_type,
            },
        )
        return username

    admins, drivers, customers = [], [], []

    # ---------------- ADMINS ----------------
    print("Populating admins...")
    for i in range(n_admins):
        if i % max(1, n_admins // 5) == 0:
            print(f"Admin {i}/{n_admins}")
        u = insert_user("ADMIN")
        admins.append(u)
        insert_auto(db, database, "administrators", {"username_administrator": u})

    # ---------------- DRIVERS ----------------
    print("Populating drivers...")
    for i in range(n_drivers):
        if i % max(1, n_drivers // 5) == 0:
            print(f"Driver {i}/{n_drivers}")
        u = insert_user("DRIVER")
        drivers.append(u)
        insert_auto(
            db,
            database,
            "delivery_drivers",
            {
                "username_delivery_driver": u,
                "vehicle": random.choice(["driving", "bicycling", "walking"]),
                "is_available": fake.boolean(),
            },
        )

    # ---------------- CUSTOMERS ----------------
    print("Populating customers...")
    for i in range(n_customers):
        if i % max(1, n_customers // 5) == 0:
            print(f"Customer {i}/{n_customers}")
        u = insert_user("CUSTOMER")
        customers.append(u)
        insert_auto(db, database, "customers", {"username_customer": u, "address": fake.address().replace("\n", ", ")})

    # ---------------- ITEMS ----------------
    print("Populating items...")
    item_ids = []
    for i in range(n_items):
        if i % max(1, n_items // 5) == 0:
            print(f"Item {i}/{n_items}")
        row = insert_auto(
            db,
            database,
            "items",
            {
                "name_item": fake.word().capitalize(),
                "price": round(random.uniform(1, 100), 2),
                "category": random.choice(["starter", "main course", "dessert", "drink"]),
                "stock": random.randint(0, 200),
                "exposed": fake.boolean(),
            },
        )
        item_ids.append(row["id_item"])

    # ---------------- ORDERS ----------------
    print("Populating orders...")
    order_ids = []
    for i in range(n_orders):
        if i % max(1, n_orders // 5) == 0:
            print(f"Order {i}/{n_orders}")
        items_json = [{"id": random.choice(item_ids), "qty": random.randint(1, 4)} for _ in range(random.randint(1, 6))]
        row = insert_auto(
            db,
            database,
            "orders",
            {
                "username_customer": random.choice(customers),
                "username_delivery_driver": random.choice(drivers),
                "address": fake.address().replace("\n", ", "),
                "items": json.dumps(items_json),
                "date_order": fake.date_between(start_date="-30d", end_date="today"),
                "time_order": fake.time(),
            },
        )
        order_ids.append(row["id_order"])

    # ---------------- DELIVERIES ----------------
    print("Populating deliveries...")
    for i in range(n_deliveries):
        if i % max(1, n_deliveries // 5) == 0:
            print(f"Delivery {i}/{n_deliveries}")
        nb = random.randint(1, 4)
        selected = random.sample(order_ids, min(nb, len(order_ids)))
        stops = [fake.address().replace("\n", ", ") for _ in selected]
        insert_auto(
            db,
            database,
            "deliveries",
            {
                "username_delivery_driver": random.choice(drivers),
                "duration": random.randint(5, 90),
                "id_orders": selected,
                "stops": stops,
                "is_accepted": fake.boolean(),
            },
        )

    print("=== Population complete ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("db_name", nargs="?", default=None, help="Specify 'test' for test database")
    args = parser.parse_args()

    database_name = "project_test_database" if args.db_name == "test" else "project_database"

    populate_db(
        n_admins=30, n_drivers=100, n_customers=250, n_items=400, n_orders=800, n_deliveries=300, database=database_name
    )
