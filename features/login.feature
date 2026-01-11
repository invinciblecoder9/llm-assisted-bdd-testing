Feature: User Login Functionality

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter valid credentials
    Then I should see the success message

  Scenario Outline: Failed login with invalid credentials
    Given I am on the login page
    When I enter invalid credentials
    Then I should see the error message

    Examples:
      | username    | password  |
      | wrongUser   | pass123   |
      | admin       | wrongPass |
      | wrongUser   | wrongPass |