-- =========================================================
-- Northwind Data Model (3NF)
-- =========================================================
-- Author: Robiul Hossain
-- Description: Normalized schema with indexing & constraints
-- =========================================================

-- Drop existing tables to allow recreation
DROP SCHEMA IF EXISTS northwind CASCADE;
CREATE SCHEMA northwind;
SET search_path TO northwind;

-- =========================================================
-- Country
-- =========================================================
CREATE TABLE country (
    country_id SERIAL PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- Region
-- =========================================================
CREATE TABLE region (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL REFERENCES country(country_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_region_country_id ON region(country_id);

-- =========================================================
-- City
-- =========================================================
CREATE TABLE city (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    region_id INT NOT NULL REFERENCES region(region_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_city_region_id ON city(region_id);

-- =========================================================
-- Customer
-- =========================================================
CREATE TABLE customer (
    customer_id VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100),
    contact_title VARCHAR(50),
    address TEXT,
    city_id INT REFERENCES city(city_id) ON DELETE SET NULL,
    postal_code VARCHAR(20),
    phone VARCHAR(30),
    fax VARCHAR(30),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_customer_city_id ON customer(city_id);
CREATE INDEX idx_customer_company_name ON customer(company_name);

-- =========================================================
-- Employee
-- =========================================================
CREATE TABLE employee (
    employee_id SERIAL PRIMARY KEY,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    title VARCHAR(50),
    title_of_courtesy VARCHAR(25),
    birth_date DATE,
    hire_date DATE,
    address TEXT,
    city_id INT REFERENCES city(city_id) ON DELETE SET NULL,
    postal_code VARCHAR(20),
    home_phone VARCHAR(30),
    extension VARCHAR(10),
    photo TEXT,
    notes TEXT,
    reports_to INT,
    photo_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_employee_city_id ON employee(city_id);
CREATE INDEX idx_employee_reports_to ON employee(reports_to);

-- =========================================================
-- Supplier
-- =========================================================
CREATE TABLE supplier (
    supplier_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100),
    contact_title VARCHAR(50),
    address TEXT,
    city_id INT REFERENCES city(city_id) ON DELETE SET NULL,
    postal_code VARCHAR(20),
    phone VARCHAR(30),
    fax VARCHAR(30),
    home_page TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_supplier_city_id ON supplier(city_id);

-- =========================================================
-- Category
-- =========================================================
CREATE TABLE category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    picture TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- Product
-- =========================================================
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    supplier_id INT REFERENCES supplier(supplier_id) ON DELETE SET NULL,
    category_id INT REFERENCES category(category_id) ON DELETE SET NULL,
    quantity_per_unit VARCHAR(50),
    unit_price NUMERIC(10, 2),
    units_in_stock SMALLINT,
    units_on_order SMALLINT,
    reorder_level SMALLINT,
    discontinued BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_product_supplier_id ON product(supplier_id);
CREATE INDEX idx_product_category_id ON product(category_id);
CREATE INDEX idx_product_name ON product(product_name);

-- =========================================================
-- Shipper
-- =========================================================
CREATE TABLE shipper (
    shipper_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =========================================================
-- Order
-- =========================================================
CREATE TABLE "order" (
    order_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(10) REFERENCES customer(customer_id) ON DELETE SET NULL,
    employee_id INT REFERENCES employee(employee_id) ON DELETE SET NULL,
    order_date DATE,
    required_date DATE,
    shipped_date DATE,
    ship_via INT REFERENCES shipper(shipper_id) ON DELETE SET NULL,
    freight NUMERIC(10, 2),
    ship_name VARCHAR(100),
    ship_city_id INT REFERENCES city(city_id) ON DELETE SET NULL,
    ship_postal_code VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_order_customer_id ON "order"(customer_id);
CREATE INDEX idx_order_employee_id ON "order"(employee_id);
CREATE INDEX idx_order_ship_via ON "order"(ship_via);
CREATE INDEX idx_order_ship_city_id ON "order"(ship_city_id);

-- =========================================================
-- Order Detail
-- =========================================================
CREATE TABLE order_detail (
    order_id INT NOT NULL REFERENCES "order"(order_id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES product(product_id) ON DELETE CASCADE,
    unit_price NUMERIC(10, 2) NOT NULL,
    quantity SMALLINT NOT NULL,
    discount REAL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (order_id, product_id)
);

CREATE INDEX idx_order_detail_product_id ON order_detail(product_id);

-- =========================================================
-- End of Schema
-- =========================================================
