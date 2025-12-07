# Enterprise QA Framework: ETL, API, UI Automation

This project demonstrates an enterprise-grade End-to-End (E2E) Quality Assurance (QA) framework for a banking domain, covering ETL, API, and UI testing. It's designed for functional and integration testing, incorporating data-driven variability and CI/CD integration.

## Features

-   **ETL Testing (MySQL):**
    -   Validates data transformations and loads between `src`, `stg`, and `dw` (data warehouse) layers.
    -   Uses `pytest-bdd` for Gherkin-style feature definitions (`.feature` files) for clear, business-readable test cases.
    -   Includes scenarios for positive data flow and graceful handling of missing raw data.
-   **API Testing (FastAPI & `pytest-bdd`):**
    -   Tests a mock banking API (FastAPI) that interacts with the `dw` layer.
    -   Verifies customer balances and transaction retrieval.
    -   Includes positive scenarios and negative testing (e.g., 404 for unknown customers).
-   **UI Testing (Playwright Python):**
    -   Automates interactions with a public banking demo application ([GlobalSQA BankingProject](https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login)).
    -   Covers key workflows like Bank Manager login, adding new customers, opening accounts, and verifying customer lists.
    -   Designed for cross-browser execution (though currently configured for Chromium in CI).
-   **E2E Pipeline Test:**
    -   A single test demonstrating a full vertical slice: seeding data in `src`, simulating ETL, querying the API, and performing a basic UI check.
-   **Data-Driven Testing:**
    -   Uses external YAML files (e.g., `data/login_cases.yaml`, `data/ach_cases.yaml`) for test data variability (though not fully implemented in all current tests, the structure is in place).
-   **CI/CD Integration (GitHub Actions):**
    -   Automated workflow (`.github/workflows/ci.yml`) to run all tests on `push` and `pull_request`.
    -   Sets up a MySQL service, Python environment, installs dependencies (including Playwright browsers), and executes ETL, API, and UI tests.
## Key Selling Points

-   **Full-Stack E2E Validation:** Demonstrates robust testing across Database (ETL), API (FastAPI), and UI (Playwright) layers, ensuring comprehensive system quality.
-   **BDD-Driven Development:** Utilizes `pytest-bdd` for clear, business-readable test scenarios, enhancing collaboration and test maintainability.
-   **Production-Ready CI/CD:** Implements GitHub Actions for automated, containerized testing, including MySQL and FastAPI services, ensuring rapid feedback and deployment confidence.
-   **Data-Driven & Scalable:** Designed with data-driven principles and modular architecture, allowing for easy expansion and adaptation to complex test data requirements.
-   **Problem-Solving & Debugging:** Showcases practical problem-solving skills through real-world challenges encountered and resolved during framework development (e.g., CI environment setup, Playwright locator strategies, API service orchestration).
## Project Structure
.
├── .github/
│ └── workflows/
│ └── ci.yml # GitHub Actions workflow for CI
├── api/
│ └── main.py # FastAPI application for banking API
├── data/
│ ├── ach_cases.yaml # Example data for ACH scenarios
│ └── login_cases.yaml # Example data for login scenarios
├── db/
│ └── init_mysql.sql # SQL script to initialize MySQL schema for CI
├── features/
│ ├── api_validation.feature # Gherkin features for API tests
│ └── etl_validation.feature # Gherkin features for ETL tests
├── pages/ # Playwright Page Objects for UI interactions
│ ├── add_customer_page.py
│ ├── base_page.py
│ ├── dashboard_page.py
│ ├── login_page.py
│ ├── open_account_page.py
│ └── customers_page.py
├── tests/
│ ├── api/
│ │ └── test_api_steps.py # Step definitions for API BDD tests
│ ├── e2e/
│ │ ├── test_end_to_end_pipeline.py # E2E test across layers
│ │ └── test_treasury_workflow.py # E2E UI workflow (placeholder)
│ ├── etl/
│ │ └── test_etl_steps.py # Step definitions for ETL BDD tests
│ └── ui/
│ ├── test_banking_manager_login.py # UI tests for banking app
│ └── test_google_smoke.py # Playwright smoke test (can be removed)
├── utils/
│ ├── config.py # Configuration (DB, API_BASE_URL)
│ ├── data_loader.py # Utility for loading data files
│ └── db_client.py # Database client for MySQL interactions
├── .gitignore # Specifies intentionally untracked files
├── pytest.ini # Pytest configuration
└── requirements.txt # Python dependencies


## Setup and Local Execution

### Prerequisites

-   Python 3.11+
-   MySQL 8.0+ (running locally on port 3307, with root user and password '080675' or configured in `utils/config.py`)
-   PyCharm (recommended IDE)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/data-qa-etl-api-ui-framework.git
cd data-qa-etl-api-ui-framework
2. Set up Python Virtual Environment and Install Dependencies

python -m venv venv
.\venv\Scripts\activate   # On Windows
# source venv/bin/activate # On macOS/Linux

pip install -r requirements.txt
playwright install --with-deps
3. Initialize MySQL Databases
Ensure your MySQL server is running. Then, execute the schema initialization script:


mysql -h 127.0.0.1 -P 3307 -uroot -proot < db/init_mysql.sql
4. Run the FastAPI Application (API Layer)
Open a terminal and start the FastAPI server. Keep this running while executing API and E2E tests.


uvicorn api.main:app --reload --port 8000
5. Run Tests Locally
Open a separate terminal (with your virtual environment activated) and run pytest:


# Run all tests
pytest

# Run specific test suites
pytest tests/etl
pytest tests/api
pytest tests/ui
pytest tests/e2e

# Run UI tests in headed mode (browser visible)
pytest tests/ui --headed
CI/CD with GitHub Actions
The .github/workflows/ci.yml workflow automatically runs all tests on every push and pull_request to the main branch. It sets up a MySQL service, installs dependencies, and executes the test suite in a clean environment.
