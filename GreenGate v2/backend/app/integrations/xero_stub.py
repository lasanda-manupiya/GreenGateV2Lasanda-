"""Mock Xero integration returning realistic UK SME transaction data (12 months)."""

from __future__ import annotations

from typing import List


def get_xero_transactions() -> List[dict]:
    """Return mock Xero-style transaction data for a typical UK SME over 12 months."""
    transactions = []

    # Utilities - Electricity (monthly)
    electricity_amounts = [420, 380, 350, 310, 290, 270, 260, 265, 290, 340, 390, 450]
    for i, amount in enumerate(electricity_amounts):
        month = f"2024-{i+1:02d}-15"
        transactions.append({
            "date": month,
            "description": "British Gas Business - Electricity supply",
            "category": "Utilities - Electricity",
            "amount": amount,
            "account_code": "6010",
            "supplier_name": "British Gas Business",
        })

    # Utilities - Natural Gas (monthly, higher in winter)
    gas_amounts = [680, 620, 480, 280, 120, 60, 45, 50, 110, 320, 540, 710]
    for i, amount in enumerate(gas_amounts):
        month = f"2024-{i+1:02d}-15"
        transactions.append({
            "date": month,
            "description": "British Gas Business - Natural gas supply",
            "category": "Utilities - Gas",
            "amount": amount,
            "account_code": "6011",
            "supplier_name": "British Gas Business",
        })

    # Vehicle Fuel - Diesel (company van, bi-weekly)
    for i in range(1, 13):
        for week in [1, 15]:
            transactions.append({
                "date": f"2024-{i:02d}-{week:02d}",
                "description": "Shell - Diesel fuel",
                "category": "Vehicle Fuel",
                "amount": 85 + (i % 3) * 10,
                "account_code": "6030",
                "supplier_name": "Shell UK",
            })

    # Vehicle Fuel - Petrol (sales car, bi-weekly)
    for i in range(1, 13):
        for week in [5, 20]:
            transactions.append({
                "date": f"2024-{i:02d}-{week:02d}",
                "description": "BP - Petrol unleaded",
                "category": "Vehicle Fuel",
                "amount": 65 + (i % 4) * 8,
                "account_code": "6030",
                "supplier_name": "BP plc",
            })

    # Business Travel - Rail (monthly)
    rail_amounts = [145, 220, 180, 95, 310, 165, 50, 85, 240, 195, 280, 120]
    for i, amount in enumerate(rail_amounts):
        if amount > 0:
            transactions.append({
                "date": f"2024-{i+1:02d}-10",
                "description": "Trainline - Rail tickets London/Birmingham",
                "category": "Business Travel - Rail",
                "amount": amount,
                "account_code": "6040",
                "supplier_name": "Trainline",
            })

    # Business Travel - Flights (quarterly)
    flights = [
        {"date": "2024-03-15", "description": "easyJet - Short-haul flight Manchester-Amsterdam", "amount": 320},
        {"date": "2024-06-20", "description": "British Airways - Domestic flight London-Edinburgh", "amount": 185},
        {"date": "2024-09-10", "description": "easyJet - Short-haul flight London-Paris", "amount": 280},
        {"date": "2024-11-18", "description": "British Airways - Domestic flight Birmingham-Glasgow", "amount": 210},
    ]
    for flight in flights:
        transactions.append({
            **flight,
            "category": "Business Travel - Flights",
            "account_code": "6041",
            "supplier_name": flight["description"].split(" - ")[0],
        })

    # Office Supplies (monthly)
    for i in range(1, 13):
        transactions.append({
            "date": f"2024-{i:02d}-05",
            "description": "Staples UK - Office supplies and stationery",
            "category": "Office Supplies",
            "amount": 120 + (i % 5) * 30,
            "account_code": "6050",
            "supplier_name": "Staples UK",
        })

    # Paper specifically (quarterly)
    for i in [1, 4, 7, 10]:
        transactions.append({
            "date": f"2024-{i:02d}-12",
            "description": "Lyreco - A4 paper and printer supplies",
            "category": "Office Supplies - Paper",
            "amount": 85 + (i % 3) * 15,
            "account_code": "6051",
            "supplier_name": "Lyreco UK",
        })

    # Courier/Logistics (monthly)
    for i in range(1, 13):
        transactions.append({
            "date": f"2024-{i:02d}-20",
            "description": "DHL Express - Courier and parcel delivery",
            "category": "Courier/Logistics",
            "amount": 250 + (i % 4) * 40,
            "account_code": "6060",
            "supplier_name": "DHL Express UK",
        })

    # Professional Services (quarterly)
    for i in [2, 5, 8, 11]:
        transactions.append({
            "date": f"2024-{i:02d}-25",
            "description": "Grant Thornton - Accounting and consulting services",
            "category": "Professional Services",
            "amount": 3500 + (i % 3) * 500,
            "account_code": "6070",
            "supplier_name": "Grant Thornton UK LLP",
        })

    # IT Equipment (twice yearly)
    transactions.extend([
        {
            "date": "2024-03-01",
            "description": "Dell Technologies - Laptop computers and monitors",
            "category": "IT Equipment",
            "amount": 4200,
            "account_code": "6080",
            "supplier_name": "Dell Technologies",
        },
        {
            "date": "2024-09-01",
            "description": "Dell Technologies - Server upgrade and IT equipment",
            "category": "IT Equipment",
            "amount": 6800,
            "account_code": "6080",
            "supplier_name": "Dell Technologies",
        },
    ])

    # Water (quarterly)
    for i in [1, 4, 7, 10]:
        transactions.append({
            "date": f"2024-{i:02d}-18",
            "description": "Severn Trent Water - Water supply",
            "category": "Utilities - Water",
            "amount": 180 + (i % 3) * 20,
            "account_code": "6012",
            "supplier_name": "Severn Trent Water",
        })

    # Waste Management (monthly)
    for i in range(1, 13):
        transactions.append({
            "date": f"2024-{i:02d}-28",
            "description": "Biffa - General waste collection and disposal",
            "category": "Waste Management",
            "amount": 320 + (i % 3) * 30,
            "account_code": "6090",
            "supplier_name": "Biffa Waste Services",
        })

    return transactions
