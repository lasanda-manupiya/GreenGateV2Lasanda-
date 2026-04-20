from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.config import settings
from app.storage.base import StorageBase

logger = logging.getLogger("sustaingate.storage")


class LocalStorage(StorageBase):
    """Local filesystem storage implementation."""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _resolve(self, path: str) -> Path:
        """Resolve a relative path against the base, preventing directory traversal."""
        resolved = (self.base_path / path).resolve()
        if not str(resolved).startswith(str(self.base_path)):
            raise ValueError("Path traversal detected")
        return resolved

    async def save(self, path: str, data: bytes) -> str:
        """Save data to the local filesystem."""
        full_path = self._resolve(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)
        logger.debug("Saved %d bytes to %s", len(data), full_path)
        return str(full_path)

    async def load(self, path: str) -> bytes:
        """Load data from the local filesystem."""
        full_path = self._resolve(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_bytes()

    async def delete(self, path: str) -> bool:
        """Delete a file from the local filesystem."""
        full_path = self._resolve(path)
        if full_path.exists():
            full_path.unlink()
            logger.debug("Deleted %s", full_path)
            return True
        return False
