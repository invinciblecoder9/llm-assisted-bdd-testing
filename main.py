import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import sys
load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found!")

genai.configure(api_key=gemini_api_key)

FEATURE_DIR = Path('features')
STEPS_DIR   = Path('steps')
FEATURE_DIR.mkdir(exist_ok=True)
STEPS_DIR.mkdir(exist_ok=True)


model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",          
    generation_config={
        "temperature": 0.3,
        "max_output_tokens": 800,
    }
)


def generate_scenarios(requirements):
    prompt = f"""
You are an expert QA engineer writing BDD tests in Gherkin format.

Business Requirements:
{requirements}

Generate a complete and valid Gherkin feature file including:
- Feature title
- At least one Scenario for successful login
- At least one Scenario Outline for failed login with Examples

Use ONLY these exact step phrases:
- Given I am on the login page
- When I enter valid credentials
- When I enter invalid credentials
- Then I should see the success message
- Then I should see the error message

Output ONLY the Gherkin content. No other text.
"""

    print("Generating Gherkin scenarios using Gemini...")
    try:
        response = model.generate_content(prompt)
        gherkin = response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")

    feature_file = FEATURE_DIR / 'login.feature'
    with open(feature_file, 'w', encoding='utf-8') as f:
        f.write(gherkin)

    print(f"✅ Gherkin generated and saved to: {feature_file}")
    return gherkin, feature_file

def validate_scenarios(gherkin):
    required = ['Feature:', 'Scenario:', 'Given', 'When', 'Then']
    missing = [item for item in required if item not in gherkin]
    
    if missing:
        report = f"INVALID - Missing Gherkin elements: {', '.join(missing)}"
        valid = False
    else:
        report = "VALID - All required Gherkin elements present"
        valid = True

    with open('validation_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"Validation Result: {report}\n\n")
        f.write("Generated Gherkin:\n")
        f.write(gherkin)

    return valid, report

def select_and_write_happy_path(full_feature_file):
    with open(full_feature_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    happy_lines = []
    in_happy_scenario = False

    for line in lines:
        lowered = line.lower()
        if line.strip().startswith('Scenario:'):
            in_happy_scenario = ('success' in lowered or 'valid' in lowered or 'happy' in lowered or 'correct' in lowered)
        
        if in_happy_scenario or line.strip().startswith('Feature:') or not line.strip().startswith('Scenario:'):
            happy_lines.append(line)

    happy_file = FEATURE_DIR / 'happy_login.feature'
    with open(happy_file, 'w', encoding='utf-8') as f:
        f.writelines(happy_lines)

    print(f"Happy path scenarios extracted to: {happy_file}")
    return happy_file

def implement_steps():
    steps_code = '''
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
'''

    steps_file = STEPS_DIR / 'login_steps.py'
    with open(steps_file, 'w', encoding='utf-8') as f:
        f.write(steps_code.strip() + '\n')

    print(f"Step definitions written to: {steps_file}")

def manual_approval(gherkin, validation_report):
    print("\n" + "="*60)
    print("GENERATED GHERKIN SCENARIOS")
    print("="*60)
    print(gherkin)
    print("\nValidation Report:", validation_report)
    print("="*60)

    approval = input("\nDo you approve execution of happy path tests? (Y/N): ").strip().lower()

    with open('approval_record.txt', 'w') as f:
        f.write(f"Manual Approval Decision: {'YES' if approval == 'y' else 'NO'}\n")
        f.write(f"User Response: {approval}\n")

    return approval == 'y'

def execute_tests(happy_feature_file):
    print("\n Executing automated happy path tests using Behave...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'behave', str(FEATURE_DIR)],   # ← this is the key change
            capture_output=True,
            text=True,
            check=True
        )
        
        with open('execution_report.txt', 'w', encoding='utf-8') as f:
            f.write("Behave Test Execution Report\n")
            f.write("="*50 + "\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\nErrors:\n")
                f.write(result.stderr)

        print(result.stdout)
        if result.stderr:
            print("Errors encountered:\n", result.stderr)
            
    except subprocess.CalledProcessError as e:
        print("Behave tests failed with exit code", e.returncode)
        print("Output:\n", e.stdout)
        print("Errors:\n", e.stderr)
    except FileNotFoundError:
        print("Python could not find the 'behave' module. Run: pip install behave")

if __name__ == '__main__':
    print("LLM-Assisted BDD Functional Testing Module")
    print("Make sure the Flask app is running on http://127.0.0.1:5000\n")

    requirements = input("Enter plain-English business requirements:\n> ")

    try:
        gherkin, full_feature = generate_scenarios(requirements)
        valid, report = validate_scenarios(gherkin)

        if not valid:
            print("Validation failed. Please check generated Gherkin.")
            exit()

        happy_feature = select_and_write_happy_path(full_feature)
        implement_steps()

        if manual_approval(gherkin, report):
            execute_tests(happy_feature)
        else:
            print("Test execution aborted by user.")

    except Exception as e:
        print(f"Error: {e}")