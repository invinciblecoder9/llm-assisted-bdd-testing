# LLM-Assisted BDD Functional Testing

## Features
- Generates Gherkin scenarios from plain English using Gemini
- Validates scenarios
- Requires manual approval before execution
- Automates happy path using Behave + Playwright

## Setup
pip install flask google-generativeai behave playwright nest_asyncio python-dotenv
playwright install

## Run
1. python app.py (in one terminal)
2. python main.py (in another)