"""
Report Generator
-----------------
Transforms raw YNAB transactions into formatted HTML email reports
with both a category summary and a full transaction list.

Uses email-safe HTML: table-based layout, inline styles only,
no flexbox, no gradients, no CSS classes, no hover effects.
Tested for Gmail, Outlook, Apple Mail, and Yahoo Mail.
"""

from datetime import date, datetime
from collections import defaultdict
from config import CURRENCY_SYMBOL


def _millis_to_currency(milliunits: int) -> str:
    """Convert YNAB milliunits to a formatted currency string."""
    amount = milliunits / 1000.0
    sign = "-" if amount < 0 else ""
    return f"{sign}{CURRENCY_SYMBOL}{abs(amount):,.2f}"


def _format_date(iso_date: str) -> str:
    """Format ISO date to a more readable form."""
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return dt.strftime("%b %d, %Y")


def _period_label(year: int, month: int, is_mtd: bool = False) -> str:
    """Create a human-readable period label."""
    dt = date(year, month, 1)
    label = dt.strftime("%B %Y")
    if is_mtd:
        today = date.today()
        label += f" (through {today.strftime('%b %d')})"
    return label


def _esc(text: str) -> str:
    """Escape HTML entities."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_report(
    transactions: list,
    year: int,
    month: int,
    is_mtd: bool = False,
) -> dict:
    """
    Generate an email report from a list of transactions.

    Args:
        transactions: List of YNAB transaction dicts.
        year: Report year.
        month: Report month.
        is_mtd: Whether this is a month-to-date (ad-hoc) report.

    Returns:
        dict with 'subject', 'plain_text', and 'html' keys.
    """
    period = _period_label(year, month, is_mtd)
    report_type = "Ad-Hoc MTD" if is_mtd else "Monthly"
    txn_count = len(transactions)
    txn_label = f"{txn_count} transaction{'s' if txn_count != 1 else ''}"

    # --- Aggregate by category ---
    category_totals = defaultdict(lambda: {"inflow": 0, "outflow": 0, "count": 0})
    grand_inflow = 0
    grand_outflow = 0

    for txn in transactions:
        cat = txn.get("category_name") or "Uncategorized"
        amount = txn.get("amount", 0)

        if amount >= 0:
            category_totals[cat]["inflow"] += amount
            grand_inflow += amount
        else:
            category_totals[cat]["outflow"] += amount
            grand_outflow += amount

        category_totals[cat]["count"] += 1

    # Sort categories by outflow (most spending first)
    sorted_cats = sorted(
        category_totals.items(),
        key=lambda x: x[1]["outflow"],
    )

    net = grand_inflow + grand_outflow

    # Colors (consistent with the transaction rows)
    inflow_color = "#2e7d32"
    outflow_color = "#c62828"
    net_color = "#2e7d32" if net >= 0 else "#c62828"

    # --- Build email-safe HTML ---
    subject = f"YNAB {report_type} Report \u2014 {period}"

    html_parts = []

    # Outer wrapper + head
    html_parts.append("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<!--[if mso]><style>table,td,th{font-family:Arial,sans-serif!important;}</style><![endif]-->
</head>
<body style="margin:0;padding:0;background-color:#f4f4f7;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;">

<!-- Outer background table -->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f4f7;">
<tr>
<td align="center" style="padding:24px 16px;">

<!-- Main container -->
<table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0" style="max-width:640px;width:100%;background-color:#ffffff;border-radius:8px;overflow:hidden;border:1px solid #e0e0e0;">
""")

    # Header
    html_parts.append(f"""
<!-- Header -->
<tr>
<td style="background-color:#1a56db;padding:28px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td style="font-family:Arial,Helvetica,sans-serif;font-size:22px;font-weight:bold;color:#ffffff;line-height:1.3;">
            YNAB {_esc(report_type)} Report
        </td>
    </tr>
    <tr>
        <td style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#c7d7f5;padding-top:4px;">
            {_esc(period)} &bull; {txn_label}
        </td>
    </tr>
    </table>
</td>
</tr>
""")

    if not transactions:
        html_parts.append("""
<!-- Empty state -->
<tr>
<td style="padding:48px 32px;text-align:center;font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#888888;">
    No transactions found for this period.
</td>
</tr>
""")
    else:
        # Summary cards (Inflow / Outflow / Net)
        html_parts.append(f"""
<!-- Summary -->
<tr>
<td style="padding:24px 32px 4px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td width="33%" valign="top" style="padding-right:6px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f1f8f2;border-radius:6px;">
            <tr>
                <td style="padding:14px 10px;text-align:center;">
                    <div style="font-family:Arial,Helvetica,sans-serif;font-size:10px;text-transform:uppercase;letter-spacing:0.5px;color:{inflow_color};margin-bottom:4px;">Inflow</div>
                    <div style="font-family:Arial,Helvetica,sans-serif;font-size:18px;font-weight:bold;color:{inflow_color};">{_millis_to_currency(grand_inflow)}</div>
                </td>
            </tr>
            </table>
        </td>
        <td width="33%" valign="top" style="padding:0 3px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#fdf1f1;border-radius:6px;">
            <tr>
                <td style="padding:14px 10px;text-align:center;">
                    <div style="font-family:Arial,Helvetica,sans-serif;font-size:10px;text-transform:uppercase;letter-spacing:0.5px;color:{outflow_color};margin-bottom:4px;">Outflow</div>
                    <div style="font-family:Arial,Helvetica,sans-serif;font-size:18px;font-weight:bold;color:{outflow_color};">{_millis_to_currency(grand_outflow)}</div>
                </td>
            </tr>
            </table>
        </td>
        <td width="33%" valign="top" style="padding-left:6px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f7fb;border-radius:6px;">
            <tr>
                <td style="padding:14px 10px;text-align:center;">
                    <div style="font-family:Arial,Helvetica,sans-serif;font-size:10px;text-transform:uppercase;letter-spacing:0.5px;color:{net_color};margin-bottom:4px;">Net</div>
                    <div style="font-family:Arial,Helvetica,sans-serif;font-size:18px;font-weight:bold;color:{net_color};">{_millis_to_currency(net)}</div>
                </td>
            </tr>
            </table>
        </td>
    </tr>
    </table>
</td>
</tr>
""")

        # Divider
        html_parts.append("""
<tr><td style="padding:16px 32px 0 32px;"><hr style="border:none;border-top:1px solid #eeeeee;margin:0;"></td></tr>
""")

        # Category summary
        html_parts.append("""
<!-- Category Summary -->
<tr>
<td style="padding:20px 32px 4px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td style="font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:bold;color:#1a56db;text-transform:uppercase;letter-spacing:0.5px;padding-bottom:12px;">
            Spending by Category
        </td>
    </tr>
    </table>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;">
    <!-- Header row -->
    <tr style="background-color:#f8f9fa;">
        <td style="padding:10px 12px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;border-bottom:2px solid #e0e0e0;">Category</td>
        <td style="padding:10px 12px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;text-align:right;border-bottom:2px solid #e0e0e0;" width="50">Txns</td>
        <td style="padding:10px 12px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;text-align:right;border-bottom:2px solid #e0e0e0;" width="110">Outflow</td>
        <td style="padding:10px 12px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;text-align:right;border-bottom:2px solid #e0e0e0;" width="110">Inflow</td>
    </tr>
""")

        for i, (cat_name, totals) in enumerate(sorted_cats):
            bg = "#ffffff" if i % 2 == 0 else "#fafafa"
            outflow_str = _millis_to_currency(totals["outflow"]) if totals["outflow"] != 0 else "\u2014"
            inflow_str = _millis_to_currency(totals["inflow"]) if totals["inflow"] != 0 else "\u2014"
            out_color = outflow_color if totals["outflow"] != 0 else "#bbbbbb"
            in_color = inflow_color if totals["inflow"] != 0 else "#bbbbbb"
            html_parts.append(f"""
    <tr style="background-color:{bg};">
        <td style="padding:9px 12px;border-bottom:1px solid #f0f0f0;">{_esc(cat_name)}</td>
        <td style="padding:9px 12px;border-bottom:1px solid #f0f0f0;text-align:right;color:#666666;">{totals['count']}</td>
        <td style="padding:9px 12px;border-bottom:1px solid #f0f0f0;text-align:right;color:{out_color};white-space:nowrap;">{outflow_str}</td>
        <td style="padding:9px 12px;border-bottom:1px solid #f0f0f0;text-align:right;color:{in_color};white-space:nowrap;">{inflow_str}</td>
    </tr>
""")

        html_parts.append("""
    </table>
</td>
</tr>
""")

        # Divider
        html_parts.append("""
<tr><td style="padding:16px 32px 0 32px;"><hr style="border:none;border-top:1px solid #eeeeee;margin:0;"></td></tr>
""")

        # Full transaction list
        html_parts.append("""
<!-- All Transactions -->
<tr>
<td style="padding:20px 32px 8px 32px;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td style="font-family:Arial,Helvetica,sans-serif;font-size:13px;font-weight:bold;color:#1a56db;text-transform:uppercase;letter-spacing:0.5px;padding-bottom:12px;">
            All Transactions
        </td>
    </tr>
    </table>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="font-family:Arial,Helvetica,sans-serif;font-size:13px;color:#333333;">
    <!-- Header row -->
    <tr style="background-color:#f8f9fa;">
        <td style="padding:10px 8px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;border-bottom:2px solid #e0e0e0;" width="85">Date</td>
        <td style="padding:10px 8px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;border-bottom:2px solid #e0e0e0;">Payee</td>
        <td style="padding:10px 8px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;border-bottom:2px solid #e0e0e0;">Category</td>
        <td style="padding:10px 8px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;border-bottom:2px solid #e0e0e0;">Memo</td>
        <td style="padding:10px 8px;font-weight:bold;font-size:11px;color:#666666;text-transform:uppercase;letter-spacing:0.3px;text-align:right;border-bottom:2px solid #e0e0e0;" width="100">Amount</td>
    </tr>
""")

        sorted_txns = sorted(transactions, key=lambda t: t["date"], reverse=True)

        for i, txn in enumerate(sorted_txns):
            bg = "#ffffff" if i % 2 == 0 else "#fafafa"
            txn_date = _format_date(txn["date"])
            payee = txn.get("payee_name") or "\u2014"
            category = txn.get("category_name") or "Uncategorized"
            memo = txn.get("memo") or ""
            amount = txn.get("amount", 0)
            amount_str = _millis_to_currency(amount)
            amount_color = "#c62828" if amount < 0 else "#2e7d32"

            html_parts.append(f"""
    <tr style="background-color:{bg};">
        <td style="padding:9px 8px;border-bottom:1px solid #f0f0f0;white-space:nowrap;">{txn_date}</td>
        <td style="padding:9px 8px;border-bottom:1px solid #f0f0f0;">{_esc(payee)}</td>
        <td style="padding:9px 8px;border-bottom:1px solid #f0f0f0;">{_esc(category)}</td>
        <td style="padding:9px 8px;border-bottom:1px solid #f0f0f0;color:#888888;">{_esc(memo)}</td>
        <td style="padding:9px 8px;text-align:right;font-weight:500;color:{amount_color};border-bottom:1px solid #f0f0f0;white-space:nowrap;">{amount_str}</td>
    </tr>
""")

        html_parts.append("""
    </table>
</td>
</tr>
""")

    # Footer
    generated_on = datetime.now().strftime("%b %d, %Y at %I:%M %p")
    html_parts.append(f"""
<!-- Footer -->
<tr>
<td style="background-color:#f8f9fa;padding:16px 32px;text-align:center;font-family:Arial,Helvetica,sans-serif;font-size:11px;color:#999999;border-top:1px solid #eeeeee;">
    Generated on {generated_on} &bull; YNAB Transaction Reporter
</td>
</tr>

</table>
<!-- /Main container -->

</td>
</tr>
</table>
<!-- /Outer background table -->

</body>
</html>
""")

    html = "".join(html_parts)

    # --- Plain text fallback ---
    plain_lines = [
        f"YNAB {report_type} Report \u2014 {period}",
        f"{txn_count} transactions",
        "",
    ]

    if transactions:
        plain_lines.append(f"Inflow:  {_millis_to_currency(grand_inflow)}")
        plain_lines.append(f"Outflow: {_millis_to_currency(grand_outflow)}")
        plain_lines.append(f"Net:     {_millis_to_currency(net)}")
        plain_lines.append("")
        plain_lines.append("--- SPENDING BY CATEGORY ---")

        for cat_name, totals in sorted_cats:
            out = _millis_to_currency(totals["outflow"]) if totals["outflow"] else "\u2014"
            plain_lines.append(f"  {cat_name}: {out} ({totals['count']} txns)")

        plain_lines.append("")
        plain_lines.append("--- ALL TRANSACTIONS ---")

        sorted_txns = sorted(transactions, key=lambda t: t["date"], reverse=True)
        for txn in sorted_txns:
            txn_date = _format_date(txn["date"])
            payee = txn.get("payee_name") or "\u2014"
            amount_str = _millis_to_currency(txn.get("amount", 0))
            category = txn.get("category_name") or "Uncategorized"
            plain_lines.append(f"  {txn_date}  {payee:<30s}  {amount_str:>12s}  [{category}]")
    else:
        plain_lines.append("No transactions found for this period.")

    return {
        "subject": subject,
        "plain_text": "\n".join(plain_lines),
        "html": html,
    }
