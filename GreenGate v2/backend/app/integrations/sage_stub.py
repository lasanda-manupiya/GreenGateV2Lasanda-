"""Mock Sage integration returning realistic UK SME transaction data."""

from __future__ import annotations

from typing import List


def get_sage_transactions() -> List[dict]:
    """Return mock Sage-style transaction data for a typical UK SME.

    Same underlying data as Xero but with Sage-specific field names.
    """
    # Reuse Xero data, map to Sage format
    from app.integrations.xero_stub import get_xero_transactions

    xero_data = get_xero_transactions()

    sage_transactions = []
    for txn in xero_data:
        sage_transactions.append({
            "date": txn["date"],
            "description": txn["description"],
            "category": txn["category"],
            "amount": txn["amount"],
            # Sage-specific field names
            "nominal_code": txn["account_code"],
            "contact_name": txn["supplier_name"],
            "transaction_type": "PI",  # Purchase Invoice
            "tax_code": "T1",  # Standard Rate VAT
            "reference": f"SAGE-{hash(txn['description']) % 100000:05d}",
            # Map to supplier_name for compatibility
            "supplier_name": txn["supplier_name"],
        })

    return sage_transactions
