from pytest_bdd import scenarios, given, when, then, parsers
from utils.config import BASE_URL
from utils import db_client
from pytest_bdd import parsers  # if not already imported at top
import pytest
pytestmark = pytest.mark.etl_smoke

# Link this file to the feature
scenarios("etl_validation.feature")


@given('raw transactions exist for customer "1001"')
def insert_raw_data():
    # Clean old data for this customer in all relevant tables
    db_client.execute("src", "DELETE FROM transactions_raw WHERE customer_id = 1001")
    db_client.execute("stg", "DELETE FROM transactions_stage WHERE customer_id = 1001")
    db_client.execute("dw", "DELETE FROM transactions_fact WHERE customer_id = 1001")

    # Insert a simple test row
    db_client.execute(
        "src",
        """
        INSERT INTO transactions_raw (customer_id, account_id, amount, currency, created_at)
        VALUES (1001, 2001, 100.00, 'USD', NOW())
        """,
    )
    # Insert another row that will be transformed
    db_client.execute(
        "src",
        """
        INSERT INTO transactions_raw (customer_id, account_id, amount, currency, created_at)
        VALUES (1001, 2002, 500.00, 'EUR', NOW())
        """,
    )


@when("the ETL job runs")
def run_etl():
    # Clear staging and fact tables for this customer before running ETL
    db_client.execute("stg", "DELETE FROM transactions_stage WHERE customer_id = 1001")
    db_client.execute("dw", "DELETE FROM transactions_fact WHERE customer_id = 1001")

    # Step 1: Copy from src to stg (staging)
    db_client.execute(
        "stg",
        """
        INSERT INTO transactions_stage (id, customer_id, account_id, amount, currency, created_at)
        SELECT id, customer_id, account_id, amount, currency, created_at
        FROM src.transactions_raw WHERE customer_id = 1001
        """,
    )

    # Step 2: Transform and load from stg to dw (fact table)
    # Transformation: Set status to 'PROCESSED' for USD transactions, 'PENDING' for others
    db_client.execute(
        "dw",
        """
        INSERT INTO transactions_fact (id, customer_id, account_id, amount, currency, created_at, status)
        SELECT
            id,
            customer_id,
            account_id,
            amount,
            currency,
            created_at,
            CASE
                WHEN currency = 'USD' THEN 'PROCESSED'
                ELSE 'PENDING'
            END AS status
        FROM stg.transactions_stage WHERE customer_id = 1001
        """,
    )


@then('staging rows match raw rows for customer "1001"')
def compare_raw_and_stage():
    raw_count = db_client.fetch_one(
        "src", "SELECT COUNT(*) FROM transactions_raw WHERE customer_id = 1001"
    )[0]
    stg_count = db_client.fetch_one(
        "stg", "SELECT COUNT(*) FROM transactions_stage WHERE customer_id = 1001"
    )[0]
    assert raw_count == stg_count, f"Raw count {raw_count} != Staging count {stg_count}"


@then('DW fact table shows correct transformations for customer "1001"')
def validate_dw_transformations():
    # Check USD transaction status
    usd_status = db_client.fetch_one(
        "dw", "SELECT status FROM transactions_fact WHERE customer_id = 1001 AND currency = 'USD'"
    )
    assert usd_status and usd_status[0] == 'PROCESSED', "USD transaction status not 'PROCESSED'"

    # Check EUR transaction status
    eur_status = db_client.fetch_one(
        "dw", "SELECT status FROM transactions_fact WHERE customer_id = 1001 AND currency = 'EUR'"
    )
    assert eur_status and eur_status[0] == 'PENDING', "EUR transaction status not 'PENDING'"

    # Check total count in DW
    dw_count = db_client.fetch_one(
        "dw", "SELECT COUNT(*) FROM transactions_fact WHERE customer_id = 1001"
    )[0]
    assert dw_count == 2, f"Expected 2 rows in DW, got {dw_count}"


@given(parsers.parse('no raw transactions exist for customer "{customer_id}"'))
def no_raw_transactions(customer_id: str):
    cid = int(customer_id)
    db_client.execute("src", f"DELETE FROM transactions_raw WHERE customer_id = {cid}")
    db_client.execute("stg", f"DELETE FROM transactions_stage WHERE customer_id = {cid}")
    db_client.execute("dw", f"DELETE FROM transactions_fact WHERE customer_id = {cid}")
    db_client.execute("dw", f"DELETE FROM customer_balances WHERE customer_id = {cid}")


@when(parsers.parse('the ETL job runs for customer "{customer_id}"'))
def run_etl_for_customer(customer_id: str):
    cid = int(customer_id)

    # simulate same ETL logic, but there is no raw data
    db_client.execute(
        "stg",
        f"""
        INSERT INTO transactions_stage (id, customer_id, account_id, amount, currency, created_at)
        SELECT id, customer_id, account_id, amount, currency, created_at
        FROM src.transactions_raw
        WHERE customer_id = {cid};
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
            CASE WHEN currency = 'USD' THEN 'PROCESSED' ELSE 'PENDING' END
        FROM stg.transactions_stage
        WHERE customer_id = {cid};
        """,
    )

    db_client.execute(
        "dw",
        f"""
        INSERT INTO customer_balances (customer_id, account_id, balance)
        SELECT
            customer_id,
            account_id,
            SUM(amount) AS balance
        FROM dw.transactions_fact
        WHERE customer_id = {cid}
        GROUP BY customer_id, account_id
        ON DUPLICATE KEY UPDATE balance = VALUES(balance);
        """,
    )


@then(parsers.parse('no staging or DW rows exist for customer "{customer_id}"'))
def no_rows_in_stg_or_dw(customer_id: str):
    cid = int(customer_id)

    stg_count = db_client.fetch_one(
        "stg", f"SELECT COUNT(*) FROM transactions_stage WHERE customer_id = {cid}"
    )[0]
    fact_count = db_client.fetch_one(
        "dw", f"SELECT COUNT(*) FROM transactions_fact WHERE customer_id = {cid}"
    )[0]
    bal_count = db_client.fetch_one(
        "dw", f"SELECT COUNT(*) FROM customer_balances WHERE customer_id = {cid}"
    )[0]

    assert stg_count == 0
    assert fact_count == 0
    assert bal_count == 0

@then(parsers.parse('the API response status is {status_code:d}'))
def api_response_status_is(status_code: int):
    assert ApiContext.status_code == status_code