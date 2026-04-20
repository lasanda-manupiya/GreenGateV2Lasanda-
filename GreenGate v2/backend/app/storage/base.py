from __future__ import annotations

from abc import ABC, abstractmethod


class StorageBase(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def save(self, path: str, data: bytes) -> str:
        """Save data to the given path. Returns the full storage path."""
        ...

    @abstractmethod
    async def load(self, path: str) -> bytes:
        """Load data from the given path. Raises FileNotFoundError if not found."""
        ...

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete data at the given path. Returns True if deleted, False if not found."""
        ...
