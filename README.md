# YNAB Transaction Reporter

Fetches transactions from your YNAB budget and emails a formatted HTML report with a **category summary** and a **full transaction list**. Transfers are excluded.

## Features

- **Monthly Report** — full report for any calendar month
- **Ad-Hoc MTD Report** — transactions from the 1st of the current month through today
- **HTML Email** — email-safe report (table-based layout, inline styles) with an inflow/outflow/net summary, category breakdown, and a detailed transaction table
- **Gmail Integration** — generates a payload compatible with the Gmail `create_draft` tool, or can send via SMTP
- **Preview Mode** — save the report as a local HTML file before sending

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your YNAB token
cp .env.example .env
#    then edit .env and set YNAB_API_TOKEN to a freshly generated token
```

The token is read from the environment (via `.env`), never hardcoded. Set `YNAB_BUDGET_ID`
and `YNAB_RECIPIENTS` in `.env` too.

## Usage

```bash
# Send current month's full report
python main.py monthly

# Send ad-hoc month-to-date report
python main.py adhoc

# Report for a specific month
python main.py monthly --year 2026 --month 3

# Preview locally (no email)
python main.py adhoc --preview

# Add extra recipients
python main.py monthly --to extra@example.com --to boss@example.com
```

## How Email Works

The script generates an `email_payload.json` file containing the subject, HTML body, plain-text body, and recipients. You can use this payload in two ways:

1. **Gmail (recommended)** — Hand the payload to the Gmail `create_draft` tool to create a draft, then review and send. In Cowork, ask Claude to draft it using your connected Gmail.
2. **SMTP** — Set `SMTP_*` environment variables and call `send_via_smtp()` directly.

## Running in Claude Cowork

This project is set up to run inside Claude Cowork (the desktop agent). See
**COWORK_SETUP.md** for the full walkthrough, and **CLAUDE.md** for the
folder instructions Cowork uses to run the two report modes.

## Project Structure

```
ynab-reporter/
├── config.py            # Loads token from .env; budget ID + recipients
├── ynab_client.py       # YNAB API client
├── report_generator.py  # Email-safe HTML / plain-text report builder
├── main.py              # CLI entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Template for your token (copy to .env)
├── .gitignore           # Keeps .env and generated reports out of git
├── CLAUDE.md            # Folder instructions for Cowork
├── COWORK_SETUP.md      # How to run this in Cowork
└── README.md            # This file
```

## Security Note

Your YNAB personal access token lives in `.env`, which is gitignored — never
commit it. Regenerate the token if it has ever been shared. To rotate it, just
update `YNAB_API_TOKEN` in `.env`.

## Adding Recipients

Set `YNAB_RECIPIENTS` in `.env` (comma-separated), or pass `--to extra@example.com`.
