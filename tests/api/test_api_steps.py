import requests
from pytest_bdd import scenarios, given, when, then, parsers
from utils.config import BASE_URL
from utils import db_client
import pytest

pytestmark = pytest.mark.api_smoke


# Link to the feature file (pytest.ini has bdd_features_base_dir = features)
scenarios("api_validation.feature")


# Use a fixture to provide an instance of ApiContext for each test
class ApiContext:
    def __init__(self):
        self.balances = None
        self.transactions = None
        self.status_code = None


@pytest.fixture
def api_context():
    return ApiContext()


@given(parsers.parse('the ETL job has run for customer "{customer_id}"'))
def etl_job_has_run(customer_id: str):
    cid = int(customer_id)

    # clean existing data
    db_client.execute("src", f"DELETE FROM transactions_raw WHERE customer_id = {cid}")
    db_client.execute("stg", f"DELETE FROM transactions_stage WHERE customer_id = {cid}")
    db_client.execute("dw", f"DELETE FROM transactions_fact WHERE customer_id = {cid}")
    db_client.execute("dw", f"DELETE FROM customer_balances WHERE customer_id = {cid}")

    # seed raw rows
    db_client.execute(
        "src",
        f"""
        INSERT INTO transactions_raw (customer_id, account_id, amount, currency, created_at)
        VALUES 
            ({cid}, 2001, 100.00, 'USD', NOW()),
            ({cid}, 2002, 500.00, 'EUR', NOW());
        """,
    )

    # ETL: src -> stg
    db_client.execute(
        "stg",
        f"""
        INSERT INTO transactions_stage (id, customer_id, account_id, amount, currency, created_at)
        SELECT id, customer_id, account_id, amount, currency, created_at
        FROM src.transactions_raw
        WHERE customer_id = {cid};
        """,
    )

    # ETL: stg -> dw.transactions_fact with status
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

    # ETL: aggregate to dw.customer_balances
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
        GROUP BY customer_id, account_id;
        """,
    )


@when(parsers.parse('I request balances for customer "{customer_id}"'))
def request_balances(customer_id: str, api_context: ApiContext):
    url = f"{BASE_URL}/customers/{customer_id}/balances"
    resp = requests.get(url)
    api_context.status_code = resp.status_code
    api_context.balances = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None


@when(parsers.parse('I request transactions for customer "{customer_id}"'))
def request_transactions(customer_id: str, api_context: ApiContext):
    url = f"{BASE_URL}/customers/{customer_id}/transactions"
    resp = requests.get(url)
    api_context.status_code = resp.status_code
    api_context.transactions = resp.json()
    assert resp.status_code == 200, f"GET {url} -> {resp.status_code}"


@then(parsers.parse('the API response contains {count:d} accounts'))
def api_response_contains_accounts(count: int, api_context: ApiContext):
    assert isinstance(api_context.balances, list)
    assert len(api_context.balances) == count


@then(parsers.parse('account "{account_id}" has a balance of {expected_balance:f}'))
def account_has_balance(account_id: str, expected_balance: float, api_context: ApiContext):
    for acc in api_context.balances:
        if str(acc["account_id"]) == account_id:
            assert acc["balance"] == expected_balance
            return
    assert False, f"Account {account_id} not found in balances"


@then(parsers.parse('the API response contains {count:d} transactions'))
def api_response_contains_transactions(count: int, api_context: ApiContext):
    assert isinstance(api_context.transactions, list)
    assert len(api_context.transactions) == count


@then(parsers.parse('transaction for account "{account_id}" has status "{expected_status}"'))
def transaction_has_status(account_id: str, expected_status: str, api_context: ApiContext):
    for tx in api_context.transactions:
        if str(tx["account_id"]) == account_id:
            assert tx["status"] == expected_status
            return
    assert False, f"Transaction for account {account_id} not found in transactions"


@then(parsers.parse('the API response status is {status_code:d}'))
def api_response_status_is(status_code: int, api_context: ApiContext):
    assert api_context.status_code == status_code