"""
Database models for the GOFAP platform data import system.
"""

from .imported_data import ImportedData, SyncStatus

__all__ = ["ImportedData", "SyncStatus"]
