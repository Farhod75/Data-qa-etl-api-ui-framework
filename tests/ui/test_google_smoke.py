import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.ui
def test_playwright_demo_todos():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Playwright's own demo site (stable)
        page.goto("https://demo.playwright.dev/todomvc", wait_until="domcontentloaded")

        # Add a todo
        page.fill("input.new-todo", "buy milk")
        page.keyboard.press("Enter")

        # Verify it appears in the list
        items = page.locator("ul.todo-list li")
        assert items.count() == 1
        assert items.nth(0).locator("label").inner_text() == "buy milk"

        browser.close()