"""
YNAB Reporter Configuration
----------------------------
Secrets are loaded from the environment so they never live in source control.

Copy .env.example to .env and fill in your token, or export the variables
in your shell / Cowork environment. All the module-level names below are
unchanged, so the rest of the project (ynab_client.py, main.py) keeps working.
"""

import os

# Load variables from a local .env file if python-dotenv is installed.
# This is optional: if the package isn't present, real environment
# variables are used directly.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and add your "
            f"credentials, or export {name} in your environment."
        )
    return value


# YNAB API Settings
YNAB_API_TOKEN = _require("YNAB_API_TOKEN")  # required, never hardcoded
YNAB_BUDGET_ID = _require("YNAB_BUDGET_ID")
YNAB_BASE_URL = os.environ.get("YNAB_BASE_URL", "https://api.ynab.com/v1")

# Email recipients: comma-separated YNAB_RECIPIENTS, or pass --to on the CLI.
EMAIL_RECIPIENTS = [
    r.strip() for r in os.environ.get("YNAB_RECIPIENTS", "").split(",") if r.strip()
]

# Report Settings
CURRENCY_SYMBOL = "$"  # Change to your currency symbol
