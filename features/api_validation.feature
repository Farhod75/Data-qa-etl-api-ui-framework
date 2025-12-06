Feature: Banking API validation

  Scenario: Customer balances can be retrieved via API
    Given the ETL job has run for customer "1001"
    When I request balances for customer "1001"
    Then the API response contains 2 accounts
    And account "2001" has a balance of 100.00
    And account "2002" has a balance of 500.00

  Scenario: Customer transactions can be retrieved via API
    Given the ETL job has run for customer "1001"
    When I request transactions for customer "1001"
    Then the API response contains 2 transactions
    And transaction for account "2001" has status "PROCESSED"
    And transaction for account "2002" has status "PENDING"

  Scenario: API returns 404 for unknown customer
    When I request balances for customer "9999"
    Then the API response status is 404