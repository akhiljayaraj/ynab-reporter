"""
YNAB API Client
----------------
Handles all communication with the YNAB API.
"""

import requests
from config import YNAB_API_TOKEN, YNAB_BUDGET_ID, YNAB_BASE_URL


class YNABClient:
    def __init__(self):
        self.base_url = YNAB_BASE_URL
        self.budget_id = YNAB_BUDGET_ID
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {YNAB_API_TOKEN}",
            "Accept": "application/json",
        })

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make a GET request to the YNAB API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_budget_info(self) -> dict:
        """Fetch basic budget info."""
        data = self._get(f"/budgets/{self.budget_id}")
        return data["data"]["budget"]

    def get_transactions(self, since_date: str = None) -> list:
        """
        Fetch all transactions, optionally filtered by since_date.

        Args:
            since_date: ISO date string (YYYY-MM-DD). Only transactions
                        on or after this date are returned.

        Returns:
            List of transaction dicts, with transfers and deleted
            transactions excluded.
        """
        params = {}
        if since_date:
            params["since_date"] = since_date

        data = self._get(f"/budgets/{self.budget_id}/transactions", params=params)
        transactions = data["data"]["transactions"]

        # Exclude transfers (they carry a transfer_account_id) and deleted txns
        return [
            t for t in transactions
            if not t.get("transfer_account_id") and not t.get("deleted")
        ]
