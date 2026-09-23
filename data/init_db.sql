DROP SCHEMA IF EXISTS project_database CASCADE;
CREATE SCHEMA project_database;

--------------------------------------------------------------
-- user
--------------------------------------------------------------
DROP TABLE IF EXISTS project_database.users CASCADE;
CREATE TABLE project_database.users (
    username VARCHAR PRIMARY KEY,
    firstname VARCHAR,
    lastname VARCHAR,
    password VARCHAR,
    salt VARCHAR,
    account_type VARCHAR
);

--------------------------------------------------------------
-- administrator
--------------------------------------------------------------
DROP TABLE IF EXISTS project_database.administrators CASCADE;
CREATE TABLE project_database.administrators (
  username_administrator VARCHAR UNIQUE NOT NULL,
  FOREIGN KEY (username_administrator) REFERENCES project_database.users(username) ON DELETE CASCADE
);

--------------------------------------------------------------
-- delivery_driver
--------------------------------------------------------------
DROP TABLE IF EXISTS project_database.delivery_drivers CASCADE;
CREATE TABLE project_database.delivery_drivers (
    username_delivery_driver TEXT PRIMARY KEY REFERENCES project_database.users(username) ON DELETE CASCADE,
    vehicle TEXT,
    is_available BOOLEAN
);
--------------------------------------------------------------
-- customer
--------------------------------------------------------------
DROP TABLE IF EXISTS project_database.customers CASCADE;
CREATE TABLE project_database.customers (
  username_customer VARCHAR UNIQUE NOT NULL,
  address VARCHAR,
  FOREIGN KEY (username_customer) REFERENCES project_database.users(username) ON DELETE CASCADE
);

--------------------------------------------------------------
-- delivery
--------------------------------------------------------------
DROP TABLE IF EXISTS project_database.deliveries CASCADE;
CREATE TABLE project_database.deliveries (
  id_delivery SERIAL PRIMARY KEY,
  username_delivery_driver VARCHAR,
  duration INTEGER,
  id_orders INTEGER[],
  stops VARCHAR[],
  is_accepted BOOLEAN,
  FOREIGN KEY (username_delivery_driver) REFERENCES project_database.users(username)
);

--------------------------------------------------------------
-- item
--------------------------------------------------------------
DROP TABLE IF EXISTS project_database.items CASCADE;
CREATE TABLE project_database.items (
  id_item SERIAL PRIMARY KEY,
  name_item VARCHAR,
  price INTEGER,
  category VARCHAR,
  stock INTEGER,
  exposed BOOLEAN
);

--------------------------------------------------------------
-- order_table
--------------------------------------------------------------
DROP TABLE IF EXISTS project_database.orders CASCADE;
CREATE TABLE project_database.orders (
  id_order SERIAL PRIMARY KEY,
  username_customer VARCHAR,
  username_delivery_driver VARCHAR,
  address VARCHAR,
  items JSONB,
  date_order DATE,
  time_order TIME,
  FOREIGN KEY (username_customer) REFERENCES project_database.users(username),
  FOREIGN KEY (username_delivery_driver) REFERENCES project_database.users(username)
);
