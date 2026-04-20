from __future__ import annotations

import csv
import io
import logging
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.carbon_auditor import categorise_transaction, GHG_CATEGORY_MAP
from app.integrations.defra_factors import DEFRAFactorsService
from app.models.emissions import EmissionsInventory

logger = logging.getLogger("sustaingate.csv_upload")

# Column alias mapping — maps various CSV header names to our canonical names
COLUMN_ALIASES: Dict[str, List[str]] = {
    "date": ["date", "transaction_date", "invoice_date", "txn_date", "period"],
    "description": ["description", "desc", "line_item", "item", "details", "narrative", "memo"],
    "supplier": ["supplier", "vendor", "supplier_name", "contact_name", "payee", "company"],
    "amount": ["amount", "total", "value", "net_amount", "net", "gross", "cost", "spend"],
    "unit": ["unit", "uom", "unit_of_measure", "units", "measure"],
    "category": ["category", "account_category", "nominal_code", "account_code", "type", "expense_type"],
}


def _normalise_header(header: str) -> str:
    """Normalise a CSV header to lowercase, stripped, underscored."""
    return header.strip().lower().replace(" ", "_").replace("-", "_")


def _map_columns(raw_headers: List[str]) -> Dict[str, Optional[str]]:
    """Map raw CSV headers to our canonical column names."""
    normalised = [_normalise_header(h) for h in raw_headers]
    mapping = {}  # type: Dict[str, Optional[str]]

    for canonical, aliases in COLUMN_ALIASES.items():
        found = None
        for alias in aliases:
            if alias in normalised:
                found = raw_headers[normalised.index(alias)]
                break
        mapping[canonical] = found

    return mapping


def parse_csv(content: bytes) -> List[dict]:
    """Parse CSV file content into normalised row dicts.

    Auto-detects encoding and maps columns via alias matching.
    Returns list of dicts with keys: date, description, supplier, amount, unit, category.
    """
    # Try UTF-8 first, fall back to Latin-1
    for encoding in ["utf-8-sig", "utf-8", "latin-1"]:
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Could not decode CSV file — unsupported encoding")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV file has no headers")

    col_map = _map_columns(list(reader.fieldnames))

    rows = []  # type: List[dict]
    for i, raw_row in enumerate(reader, start=2):  # start=2 because row 1 is headers
        row = {
            "row_number": i,
            "date": raw_row.get(col_map["date"] or "", "").strip() if col_map["date"] else "",
            "description": raw_row.get(col_map["description"] or "", "").strip() if col_map["description"] else "",
            "supplier": raw_row.get(col_map["supplier"] or "", "").strip() if col_map["supplier"] else "",
            "amount": raw_row.get(col_map["amount"] or "", "").strip() if col_map["amount"] else "",
            "unit": raw_row.get(col_map["unit"] or "", "").strip() if col_map["unit"] else "",
            "category": raw_row.get(col_map["category"] or "", "").strip() if col_map["category"] else "",
        }
        # Skip completely empty rows
        if not any([row["description"], row["amount"]]):
            continue
        # Parse amount to float
        try:
            amount_str = row["amount"].replace(",", "").replace("£", "").replace("$", "").strip()
            row["amount_value"] = float(amount_str) if amount_str else 0.0
        except ValueError:
            row["amount_value"] = 0.0
        rows.append(row)

    return rows


def categorise_rows(rows: List[dict]) -> Tuple[List[dict], List[dict]]:
    """Categorise parsed CSV rows using GHG category mapping.

    Returns (categorised, uncategorised) where categorised rows have
    ghg_scope, ghg_category, and defra_key added.
    """
    categorised = []  # type: List[dict]
    uncategorised = []  # type: List[dict]

    for row in rows:
        txn = {"description": row["description"], "category": row["category"]}
        category_key = categorise_transaction(txn)

        if category_key and category_key in GHG_CATEGORY_MAP:
            mapping = GHG_CATEGORY_MAP[category_key]
            row["ghg_scope"] = mapping["scope"]
            row["ghg_category"] = mapping["ghg_category"]
            row["defra_key"] = mapping["defra_key"]
            categorised.append(row)
        else:
            uncategorised.append(row)

    return categorised, uncategorised


async def process_csv_upload(
    db: AsyncSession,
    org_id: str,
    reporting_year: int,
    content: bytes,
) -> dict:
    """Process a CSV upload end-to-end: parse, categorise, apply DEFRA factors, create DB entries."""
    rows = parse_csv(content)
    categorised, uncategorised = categorise_rows(rows)

    defra = DEFRAFactorsService()

    # Aggregate by GHG category
    aggregated = {}  # type: Dict[str, dict]
    for row in categorised:
        key = row["ghg_category"]
        if key not in aggregated:
            aggregated[key] = {
                "scope": row["ghg_scope"],
                "category": key,
                "defra_key": row["defra_key"],
                "total_amount": Decimal("0"),
                "transaction_count": 0,
            }
        aggregated[key]["total_amount"] += Decimal(str(row["amount_value"]))
        aggregated[key]["transaction_count"] += 1

    # Apply DEFRA factors and create entries
    entries_created = []  # type: List[dict]
    for key, agg in aggregated.items():
        factor_data = defra.get_factor_by_key(agg["defra_key"])
        if not factor_data:
            logger.warning("No DEFRA factor found for key: %s", agg["defra_key"])
            continue

        factor_value = Decimal(str(factor_data["factor_value"]))
        activity_data = agg["total_amount"]
        co2e_kg = activity_data * factor_value
        co2e_tonnes = co2e_kg / Decimal("1000")

        entry = EmissionsInventory(
            id=str(uuid.uuid4()),
            organisation_id=org_id,
            reporting_year=reporting_year,
            scope=agg["scope"],
            category=agg["category"],
            source="CSV Upload",
            activity_data=activity_data,
            activity_unit=factor_data["unit"],
            emission_factor=factor_value,
            emission_factor_source="DEFRA/DESNZ %s" % factor_data["year"],
            co2e_tonnes=round(co2e_tonnes, 6),
            confidence_tier="medium",
            data_source="csv_upload",
            notes="Imported from CSV (%d transactions)" % agg["transaction_count"],
        )
        db.add(entry)
        entries_created.append({
            "scope": agg["scope"],
            "category": agg["category"],
            "activity_data": float(activity_data),
            "activity_unit": factor_data["unit"],
            "emission_factor": float(factor_value),
            "co2e_tonnes": float(round(co2e_tonnes, 6)),
            "transaction_count": agg["transaction_count"],
        })

    await db.flush()

    total_co2e = sum(e["co2e_tonnes"] for e in entries_created)

    return {
        "entries_created": len(entries_created),
        "categorised_count": len(categorised),
        "uncategorised_count": len(uncategorised),
        "total_co2e_tonnes": round(total_co2e, 4),
        "entries": entries_created,
        "uncategorised": [
            {
                "row_number": r["row_number"],
                "description": r.get("description", ""),
                "amount": r.get("amount_value", 0),
                "category": r.get("category", ""),
            }
            for r in uncategorised
        ],
    }


async def process_folder(
    db: AsyncSession,
    org_id: str,
    reporting_year: int,
    folder_path: str,
) -> dict:
    """Scan a folder for CSV files and process each one."""
    path = Path(folder_path).resolve()
    if not path.exists():
        raise ValueError("Folder does not exist: %s" % folder_path)
    if not path.is_dir():
        raise ValueError("Path is not a directory: %s" % folder_path)

    csv_files = sorted(path.glob("*.csv"))
    if not csv_files:
        raise ValueError("No CSV files found in: %s" % folder_path)

    file_results = []  # type: List[dict]
    total_entries = 0
    total_co2e = 0.0

    for csv_file in csv_files:
        try:
            content = csv_file.read_bytes()
            result = await process_csv_upload(db, org_id, reporting_year, content)
            file_results.append({
                "filename": csv_file.name,
                "entries_created": result["entries_created"],
                "co2e_tonnes": result["total_co2e_tonnes"],
                "errors": None,
            })
            total_entries += result["entries_created"]
            total_co2e += result["total_co2e_tonnes"]
        except Exception as e:
            logger.error("Error processing %s: %s", csv_file.name, str(e))
            file_results.append({
                "filename": csv_file.name,
                "entries_created": 0,
                "co2e_tonnes": 0,
                "errors": str(e),
            })

    return {
        "files_processed": len(csv_files),
        "total_entries_created": total_entries,
        "total_co2e_tonnes": round(total_co2e, 4),
        "file_results": file_results,
    }
