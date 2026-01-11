"""
Data Module for CircleNClick

This module handles loading and processing of fact-checking datasets
from various public sources (FEVER, LIAR, etc.) and cloud APIs.
"""

from data.dataset_loader import DatasetLoader, get_dataset_loader

__all__ = [
    "DatasetLoader",
    "get_dataset_loader",
]
