# YNAB Transaction Reporter — Cowork Instructions

This folder is a Python project that fetches transactions from YNAB, builds a
formatted, email-safe HTML report, and creates a Gmail draft.

## What you can ask for

- **Monthly report** — full report for the current calendar month.
- **Month-to-date (MTD) report** — transactions from the 1st of the current
  month through today.

Both group transactions by category with totals and include a full transaction
list. Transfers are excluded.

## How to run it

From this folder:

```bash
pip install -r requirements.txt              # first run only
python main.py monthly                        # full current-month report
python main.py adhoc                          # month-to-date report
python main.py adhoc --preview                # save HTML locally, no email
python main.py monthly --year 2026 --month 3  # a specific month
```

Running the script produces the report HTML and an `email_payload.json`
(subject, htmlBody, plain body, recipients).

## Email step

After generating the payload, create a Gmail **draft** using the connected Gmail
tool with the payload's subject, recipients, and `htmlBody`. Do not send
automatically — leave it as a draft for review unless I explicitly ask you to
send it.

## Environment notes

- The YNAB token lives in `.env` (`YNAB_API_TOKEN`). Never print it, commit it,
  or include it in any output.
- `api.ynab.com` must be in Cowork's allowed network domains, or the fetch will
  be blocked. This does not affect the Gmail step, which goes through a connector.
- Budget ID and recipients default in `config.py` and can be overridden via env.
- The standard `requests` call works fine here — no curl workaround is needed in
  this environment. If a YNAB call fails, just retry once.
