DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Transactions;
DROP TABLE IF EXISTS Redemptions;

CREATE TABLE Customers (
    customer_id TEXT,
    join_date TEXT,
    loyalty_tier TEXT,
    age INTEGER,
    gender TEXT,
    city TEXT,
    email TEXT
);

CREATE TABLE Products (
    product_id TEXT,
    product_type TEXT,
    model_or_flavor TEXT,
    flavor TEXT,
    intensity TEXT,
    price_eur REAL
);

CREATE TABLE Transactions (
    transaction_id TEXT,
    customer_id TEXT,
    product_id TEXT,
    quantity INTEGER,
    transaction_date TEXT,
    channel TEXT,
    total_amount_eur REAL
);

CREATE TABLE Redemptions (
    redemption_id TEXT,
    customer_id TEXT,
    redemption_date TEXT,
    reward_type TEXT,
    value_eur REAL
);
