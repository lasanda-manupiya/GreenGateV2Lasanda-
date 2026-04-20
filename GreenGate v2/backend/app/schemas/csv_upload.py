from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class CsvUploadEntry(BaseModel):
    scope: int
    category: str
    activity_data: float
    activity_unit: str
    emission_factor: float
    co2e_tonnes: float
    transaction_count: int


class UncategorisedRow(BaseModel):
    row_number: int
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None


class CsvUploadResponse(BaseModel):
    entries_created: int
    categorised_count: int
    uncategorised_count: int
    total_co2e_tonnes: float
    entries: List[CsvUploadEntry]
    uncategorised: List[UncategorisedRow]


class FolderScanRequest(BaseModel):
    folder_path: str
    reporting_year: int = 2025


class FileResult(BaseModel):
    filename: str
    entries_created: int
    co2e_tonnes: float
    errors: Optional[str] = None


class FolderScanResponse(BaseModel):
    files_processed: int
    total_entries_created: int
    total_co2e_tonnes: float
    file_results: List[FileResult]
