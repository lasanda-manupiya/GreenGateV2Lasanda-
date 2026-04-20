"""Service for loading and querying DEFRA 2025 emission factors."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("sustaingate.defra")

DATA_FILE = Path(__file__).parent.parent / "data" / "defra_2025.json"


class EmissionFactor:
    """Represents a single DEFRA emission factor."""

    def __init__(self, data: dict):
        self.key = data["key"]
        self.category = data["category"]
        self.unit = data["unit"]
        self.factor_value = data["factor_value"]
        self.co2e_unit = data["co2e_unit"]
        self.source = data["source"]
        self.year = data["year"]
        self.scope = data.get("scope")
        self.notes = data.get("notes", "")

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "category": self.category,
            "unit": self.unit,
            "factor_value": self.factor_value,
            "co2e_unit": self.co2e_unit,
            "source": self.source,
            "year": self.year,
            "scope": self.scope,
            "notes": self.notes,
        }


class DEFRAFactorsService:
    """Loads and provides access to DEFRA 2025 emission factors."""

    def __init__(self):
        self._factors: Dict[str, dict] = {}
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        try:
            with open(DATA_FILE) as f:
                data = json.load(f)
            for factor in data.get("factors", []):
                self._factors[factor["key"]] = factor
            self._loaded = True
            logger.info("Loaded %d DEFRA emission factors", len(self._factors))
        except FileNotFoundError:
            logger.warning("DEFRA factors file not found at %s", DATA_FILE)
            self._loaded = True
        except Exception as e:
            logger.error("Failed to load DEFRA factors: %s", e)
            self._loaded = True

    def get_factor(self, category: str, unit: str) -> Optional[EmissionFactor]:
        """Look up a factor by category name and unit."""
        self._load()
        for factor_data in self._factors.values():
            if (
                factor_data["category"].lower() == category.lower()
                and factor_data["unit"].lower() == unit.lower()
            ):
                return EmissionFactor(factor_data)
        return None

    def get_factor_by_key(self, key: str) -> Optional[dict]:
        """Look up a factor by its unique key."""
        self._load()
        return self._factors.get(key)

    def get_all_categories(self) -> List[str]:
        """Return all available category names."""
        self._load()
        return sorted(set(f["category"] for f in self._factors.values()))

    def get_all_factors(self) -> List[EmissionFactor]:
        """Return all factors as EmissionFactor objects."""
        self._load()
        return [EmissionFactor(f) for f in self._factors.values()]
