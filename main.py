"""
YNAB Reporter — CLI entry point
--------------------------------
Two modes:
  monthly  full report for a calendar month (defaults to the current month)
  adhoc    month-to-date: the 1st of the current month through today

Examples:
  python main.py monthly
  python main.py adhoc
  python main.py monthly --year 2026 --month 3
  python main.py adhoc --preview
  python main.py monthly --to extra@example.com --to boss@example.com
"""

import argparse
import json
import sys
from calendar import monthrange
from datetime import date
from pathlib import Path

from config import EMAIL_RECIPIENTS
from ynab_client import YNABClient
from report_generator import generate_report


def send_via_gmail_api(subject, html_body, plain_body, recipients):
    """
    Write an email_payload.json that can be handed to the Gmail
    `create_draft` tool (fields: to, subject, body, htmlBody).
    """
    payload = {
        "to": recipients,
        "subject": subject,
        "body": plain_body,
        "htmlBody": html_body,
    }
    out = Path("email_payload.json")
    out.write_text(json.dumps(payload, indent=2))
    print(f"Email payload written to {out}")
    return payload


def send_via_smtp(subject, html_body, plain_body, recipients):
    """
    Optional: send directly over SMTP. Reads settings from the environment:
      SMTP_HOST, SMTP_PORT (default 587), SMTP_USER, SMTP_PASSWORD, SMTP_FROM
    Not called by default — the Gmail payload flow is the primary path.
    """
    import os
    import smtplib
    import ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    host = os.environ.get("SMTP_HOST")
    if not host:
        raise RuntimeError("SMTP_HOST is not set; configure SMTP_* env vars to use SMTP.")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    sender = os.environ.get("SMTP_FROM", user)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(host, port) as server:
        server.starttls(context=ssl.create_default_context())
        if user and password:
            server.login(user, password)
        server.sendmail(sender, recipients, msg.as_string())
    print(f"Sent via SMTP to {', '.join(recipients)}")


def main():
    parser = argparse.ArgumentParser(description="YNAB transaction reporter")
    parser.add_argument(
        "mode",
        choices=["monthly", "adhoc"],
        help="monthly = full calendar month; adhoc = 1st of current month through today",
    )
    parser.add_argument("--year", type=int, help="Year for monthly mode (default: current)")
    parser.add_argument("--month", type=int, help="Month 1-12 for monthly mode (default: current)")
    parser.add_argument("--to", action="append", default=[], help="Extra recipient (repeatable)")
    parser.add_argument("--preview", action="store_true", help="Save HTML locally instead of emailing")
    args = parser.parse_args()

    today = date.today()

    if args.mode == "monthly":
        year = args.year or today.year
        month = args.month or today.month
        is_mtd = False
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
    else:  # adhoc — month-to-date
        year, month = today.year, today.month
        is_mtd = True
        start = date(year, month, 1)
        end = today

    since_date = start.isoformat()

    # --- Fetch ---
    client = YNABClient()
    print(f"Fetching transactions since {since_date}...")
    transactions = client.get_transactions(since_date=since_date)

    # Keep only transactions within the reporting window
    end_iso = end.isoformat()
    transactions = [t for t in transactions if since_date <= t["date"] <= end_iso]
    print(f"{len(transactions)} transactions in range.")

    # --- Generate report ---
    report = generate_report(transactions, year, month, is_mtd=is_mtd)

    # --- Output ---
    if args.preview:
        preview_path = Path(f"report_{year}_{month:02d}{'_mtd' if is_mtd else ''}.html")
        preview_path.write_text(report["html"])
        print(f"Preview saved to {preview_path}")
        return

    # Combine configured + CLI recipients
    recipients = list(set(EMAIL_RECIPIENTS + args.to))

    if not recipients:
        print("Error: no email recipients configured.", file=sys.stderr)
        sys.exit(1)

    # Save email payload for Gmail MCP
    payload = send_via_gmail_api(
        subject=report["subject"],
        html_body=report["html"],
        plain_body=report["plain_text"],
        recipients=recipients,
    )

    print("\nDone! You can now use this payload with Gmail MCP or send via SMTP.")
    print("To use SMTP instead, configure credentials and call send_via_smtp().")


if __name__ == "__main__":
    main()
