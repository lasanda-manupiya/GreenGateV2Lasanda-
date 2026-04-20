from __future__ import annotations

import copy
import re
from typing import List, Union


class RedactionEngine:
    """Redacts sensitive data from payloads before they leave the governance boundary."""

    # Patterns for UK-specific PII
    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_PATTERN = re.compile(
        r"(?:\+44|0)\s*(?:\d[\s-]*){9,10}"
    )
    NI_NUMBER_PATTERN = re.compile(
        r"[A-CEGHJ-PR-TW-Z]{2}\s*\d{2}\s*\d{2}\s*\d{2}\s*[A-D]",
        re.IGNORECASE,
    )
    POSTCODE_PATTERN = re.compile(
        r"[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}",
        re.IGNORECASE,
    )

    # Common supplier name fields
    SUPPLIER_FIELDS = {"supplier_name", "supplier", "vendor_name", "vendor", "company_name"}

    def __init__(self):
        self.last_redacted: List[str] = []
        self._supplier_counter = 0

    def redact(self, data: dict) -> dict:
        """Return a deep copy of data with sensitive fields redacted."""
        self.last_redacted = []
        self._supplier_counter = 0
        return self._redact_recursive(copy.deepcopy(data), path="")

    def _redact_recursive(self, obj: Union[dict, list, str], path: str = "") -> Union[dict, list, str]:
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key

                # Check if key is a supplier name field
                if key.lower() in self.SUPPLIER_FIELDS and isinstance(value, str):
                    self._supplier_counter += 1
                    result[key] = f"Supplier #{self._supplier_counter}"
                    self.last_redacted.append(current_path)
                elif isinstance(value, str):
                    result[key] = self._redact_string(value, current_path)
                elif isinstance(value, dict):
                    result[key] = self._redact_recursive(value, current_path)
                elif isinstance(value, list):
                    result[key] = self._redact_recursive(value, current_path)
                else:
                    result[key] = value
            return result
        elif isinstance(obj, list):
            return [
                self._redact_recursive(item, f"{path}[{i}]")
                for i, item in enumerate(obj)
            ]
        elif isinstance(obj, str):
            return self._redact_string(obj, path)
        return obj

    def _redact_string(self, value: str, path: str) -> str:
        original = value

        # Redact email addresses
        if self.EMAIL_PATTERN.search(value):
            value = self.EMAIL_PATTERN.sub("[EMAIL REDACTED]", value)

        # Redact phone numbers
        if self.PHONE_PATTERN.search(value):
            value = self.PHONE_PATTERN.sub("[PHONE REDACTED]", value)

        # Redact NI numbers
        if self.NI_NUMBER_PATTERN.search(value):
            value = self.NI_NUMBER_PATTERN.sub("[NI NUMBER REDACTED]", value)

        # Redact postcodes
        if self.POSTCODE_PATTERN.search(value):
            value = self.POSTCODE_PATTERN.sub("[POSTCODE REDACTED]", value)

        if value != original:
            self.last_redacted.append(path)

        return value
