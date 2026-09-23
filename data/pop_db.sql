-- Users
-- password is "hardpwd123" hashed via PasswordService
INSERT INTO project_database.users (username, password, firstname, lastname, salt, account_type) 
VALUES
('aliceasm', 'd1f4dc5d8af8b647fe8c9c4ac5ad7fa11dff7e432a4957fffdfd72e8d301f1c1', 'Alice', 'Asm', '1', 'Administrator'),
('bobbia', 'b065cf2aa43d057280eca6bd79026ca38663e4e4f9572bb1916ff02759981331', 'Bob', 'Bia', '2', 'Customer'),
('charliz', 'b4a60bf401a1d7a0a41f030384ee5adfc86d404da8a195222428bebaeb945ef5', 'Charles', 'Chic', '3', 'Customer'),
('drdavid', '7cda204ee3ba0db9a1bae13a315cec9774e4afb4f6bfa9ad0c6366ee24d6b99e', 'David', 'Douze', '4', 'Customer'),
('ernesto', '1874a1ea895af317b69226428de014ce1ee9bd1df4b3f0f578906bc316a35387', 'Ernest', 'Eagle', '5', 'DeliveryDriver'),
('ernesto1', '9a1e31ce0c6b87324d7ac5e517d24c94198ac78f22ca7aa9791bb91f9e0c727c', 'Ernest', 'Eagle', '6', 'DeliveryDriver'),
('fabriccio', '65aa9251ff18bafae63a0dcd923719e2410d8c70af4a8bee53be33b881d182db', 'Fabrice', 'Fantastic', '7', 'Administrator');

-- Administrators
INSERT INTO project_database.administrators  (username_administrator) 
VALUES
('aliceasm'),
('fabriccio');

-- Customers
INSERT INTO project_database.customers  (username_customer, address) 
VALUES
('bobbia', '13 Main St.'),
('charliz', '4 Salty Spring Av.'),
('drdavid', 'Flat 5, Beverly Hills');

-- Delivery drivers
INSERT INTO project_database.delivery_drivers (username_delivery_driver, vehicle, is_available)
VALUES
('ernesto', 'driving', False),
('ernesto1', 'walking', True);

-- Items
INSERT INTO project_database.items (name_item, price, category, stock, exposed)
VALUES 
('galette saucisse', 320, 'main dish', 102, True),
('vegetarian galette', 300, 'main dish', 30, False),
('cola', 200, 'drink', 501, True);

-- Orders with string keys in items (adapted for tests)
INSERT INTO project_database.orders (username_customer, username_delivery_driver, address, items)
VALUES 
('bobbia', 'ernesto1', '13 Main St.', '{"item1":2,"item3":1}'::jsonb),
('bobbia', 'ernesto', '13 Main St.', '{"item1":39}'::jsonb),
('charliz', 'ernesto1', '4 Salty Spring Av.', '{"item1":39,"item3":2}'::jsonb);

-- Deliveries
INSERT INTO project_database.deliveries (username_delivery_driver, duration, id_orders, stops, is_accepted)
VALUES 
('bobbia', '50', ARRAY[1, 2], ARRAY['Bruz', 'Chartres de bretagne'], False),
('charliz', '15', ARRAY[1], ARRAY['Bruz.'], False);

SELECT setval(
  pg_get_serial_sequence('project_database.deliveries', 'id_delivery'),
  (SELECT MAX(id_delivery) FROM project_database.deliveries)
);