from behave import given, when, then
from playwright.sync_api import sync_playwright

playwright = None
browser = None
page = None

@given('I am on the login page')
def step_go_to_login(context):
    global playwright, browser, page
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://127.0.0.1:5000")
    page.wait_for_load_state('networkidle')

@when('I enter valid credentials')
def step_enter_valid(context):
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', 'pass123')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')

@when('I enter invalid credentials')
def step_enter_invalid(context):
    page.fill('input[name="username"]', 'wrong')
    page.fill('input[name="password"]', 'wrong')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')

@then('I should see the dashboard')
def step_see_dashboard(context):
    content = page.content().lower()
    assert "successful" in content or "welcome" in content or "dashboard" in content
    browser.close()
    playwright.stop()

@then('I should see an error message')
def step_see_error(context):
    assert "invalid" in page.content().lower() or "error" in page.content().lower()
    browser.close()
    playwright.stop()
