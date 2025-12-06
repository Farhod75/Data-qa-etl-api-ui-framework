Feature: ETL mapping validation

  Scenario: Raw data moves to staging unchanged
    Given raw transactions exist for customer "1001"
    When the ETL job runs
    Then staging rows match raw rows for customer "1001"

  Scenario: Raw data moves to staging unchanged
    Given raw transactions exist for customer "1001"
    When the ETL job runs
    Then staging rows match raw rows for customer "1001"

  Scenario: DW fact table correctly transforms transaction status
    Given raw transactions exist for customer "1001"
    When the ETL job runs
    Then DW fact table shows correct transformations for customer "1001"

  Scenario: ETL handles missing raw data gracefully
    Given no raw transactions exist for customer "9999"
    When the ETL job runs for customer "9999"
    Then no staging or DW rows exist for customer "9999"