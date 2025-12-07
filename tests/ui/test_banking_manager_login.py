import pytest
import uuid
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login"


def login_as_manager(page):
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.get_by_role("button", name="Bank Manager Login").click()
    page.wait_for_url("**/manager", timeout=5000)


@pytest.mark.ui
@pytest.mark.ui_smoke
def test_bank_manager_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        login_as_manager(page)

        add_customer_button = page.get_by_role("button", name="Add Customer")
        expect(add_customer_button).to_be_visible(timeout=5000)

        browser.close()


@pytest.mark.ui
def test_add_customer_open_account_and_verify_in_customers():
    first_name = "Bank"
    last_name = "Tester" + uuid.uuid4().hex[:6]  # unique per run
    post_code = "1111"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1) Login as Bank Manager
        login_as_manager(page)

        # 2) Add Customer
        page.get_by_role("button", name="Add Customer").click()
        page.get_by_placeholder("First Name").fill(first_name)
        page.get_by_placeholder("Last Name").fill(last_name)
        page.get_by_placeholder("Post Code").fill(post_code)

        def handle_add_customer(dialog):
            assert "Customer added successfully" in dialog.message
            dialog.accept()

        page.once("dialog", handle_add_customer)
        # Use form-specific locator to avoid ambiguity
        page.locator("form button[type='submit']").click()

        # 3) Open Account for that new customer
        page.get_by_role("button", name="Open Account").click()
        page.select_option("#userSelect", label=f"{first_name} {last_name}")
        page.select_option("#currency", "Dollar")

        def handle_open_account(dialog):
            assert "Account created successfully" in dialog.message
            dialog.accept()

        page.once("dialog", handle_open_account)
        page.get_by_role("button", name="Process").click()

        # 4) Verify customer appears in Customers list
        page.get_by_role("button", name="Customers").click()
        page.get_by_placeholder("Search Customer").fill(last_name)

        rows = page.locator("table tbody tr")
        expect(rows).to_have_count(1)

        first_cell = rows.nth(0).locator("td").nth(0)
        last_cell = rows.nth(0).locator("td").nth(1)
        expect(first_cell).to_have_text(first_name)
        expect(last_cell).to_have_text(last_name)

        browser.close()