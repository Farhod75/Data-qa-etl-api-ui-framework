-- Create databases
CREATE DATABASE IF NOT EXISTS src;
CREATE DATABASE IF NOT EXISTS stg;
CREATE DATABASE IF NOT EXISTS dw;

-- Use src and create table
USE src;
CREATE TABLE IF NOT EXISTS transactions_raw (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    account_id  INT,
    amount      DECIMAL(12,2),
    currency    VARCHAR(3),
    created_at  DATETIME
);

-- Use stg and create table
USE stg;
CREATE TABLE IF NOT EXISTS transactions_stage (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    account_id  INT,
    amount      DECIMAL(12,2),
    currency    VARCHAR(3),
    created_at  DATETIME
);

-- Use dw and create tables
USE dw;
CREATE TABLE IF NOT EXISTS transactions_fact (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    account_id  INT,
    amount      DECIMAL(12,2),
    currency    VARCHAR(3),
    created_at  DATETIME,
    status      VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS customer_balances (
    customer_id INT,
    account_id  INT,
    balance     DECIMAL(12,2),
    PRIMARY KEY (customer_id, account_id)
);