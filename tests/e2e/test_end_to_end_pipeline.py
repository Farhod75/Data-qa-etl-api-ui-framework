import pytest
import requests
from playwright.sync_api import sync_playwright

from utils.config import BASE_URL
from utils import db_client


@pytest.mark.e2e
def test_etl_api_ui_pipeline():
    customer_id = 1002

    # 1) Seed raw data in src
    db_client.execute("src", f"DELETE FROM transactions_raw WHERE customer_id = {customer_id}")
    db_client.execute("stg", f"DELETE FROM transactions_stage WHERE customer_id = {customer_id}")
    db_client.execute("dw", f"DELETE FROM transactions_fact WHERE customer_id = {customer_id}")
    db_client.execute("dw", f"DELETE FROM customer_balances WHERE customer_id = {customer_id}")

    db_client.execute(
        "src",
        f"""
        INSERT INTO transactions_raw (customer_id, account_id, amount, currency, created_at)
        VALUES 
            ({customer_id}, 3001, 250.00, 'USD', NOW()),
            ({customer_id}, 3002, 750.00, 'USD', NOW());
        """,
    )

    # 2) Run a minimal ETL: src -> stg -> dw, aggregate balances
    db_client.execute(
        "stg",
        f"""
        INSERT INTO transactions_stage (id, customer_id, account_id, amount, currency, created_at)
        SELECT id, customer_id, account_id, amount, currency, created_at
        FROM src.transactions_raw
        WHERE customer_id = {customer_id};
        """,
    )

    db_client.execute(
        "dw",
        f"""
        INSERT INTO transactions_fact (id, customer_id, account_id, amount, currency, created_at, status)
        SELECT
            id,
            customer_id,
            account_id,
            amount,
            currency,
            created_at,
            'PROCESSED'
        FROM stg.transactions_stage
        WHERE customer_id = {customer_id};
        """,
    )

    db_client.execute(
        "dw",
        f"""
        INSERT INTO customer_balances (customer_id, account_id, balance)
        SELECT customer_id, account_id, SUM(amount) AS balance
        FROM dw.transactions_fact
        WHERE customer_id = {customer_id}
        GROUP BY customer_id, account_id;
        """,
    )

    # 3) Call API to verify balances
    resp = requests.get(f"{BASE_URL}/customers/{customer_id}/balances")
    assert resp.status_code == 200
    balances = resp.json()
    assert len(balances) == 2

    # Check one concrete balance
    acct_3001 = next(b for b in balances if b["account_id"] == 3001)
    assert acct_3001["balance"] == 250.0

    # 4) Do a tiny UI check (on Playwright demo site) to show UI layer is alive
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://demo.playwright.dev/todomvc", wait_until="domcontentloaded")
        assert "TodoMVC" in page.title()
        browser.close()