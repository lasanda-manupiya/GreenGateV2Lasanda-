from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.csv_upload import (
    CsvUploadResponse,
    FolderScanRequest,
    FolderScanResponse,
)
from app.services.csv_upload_service import process_csv_upload, process_folder

logger = logging.getLogger("sustaingate.api.csv_upload")

router = APIRouter(prefix="/emissions/upload", tags=["emissions-upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/csv", response_model=CsvUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    reporting_year: int = Query(2025),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("editor")),
):
    """Upload a CSV file of invoices/transactions and create emissions inventory entries.

    The CSV columns are auto-detected. Supported column names include:
    - date, transaction_date, invoice_date
    - description, desc, line_item, narrative
    - supplier, vendor, supplier_name, contact_name
    - amount, total, value, net_amount, cost
    - unit, uom
    - category, account_category, nominal_code, expense_type
    """
    # Validate file type
    if file.filename and not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported. Please upload a .csv file.",
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10 MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty.",
        )

    try:
        result = await process_csv_upload(
            db=db,
            org_id=user.organisation_id,
            reporting_year=reporting_year,
            content=content,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("CSV upload failed: %s", str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process CSV file: %s" % str(e),
        )


@router.post("/folder", response_model=FolderScanResponse, status_code=status.HTTP_201_CREATED)
async def scan_folder(
    body: FolderScanRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Scan a server-side folder for CSV invoice files and process them all.

    Requires admin role as it accesses the server filesystem.
    """
    try:
        result = await process_folder(
            db=db,
            org_id=user.organisation_id,
            reporting_year=body.reporting_year,
            folder_path=body.folder_path,
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Folder scan failed: %s", str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process folder: %s" % str(e),
        )
