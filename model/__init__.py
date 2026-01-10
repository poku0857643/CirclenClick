"""
ML Models for Content Verification

This module contains machine learning models for claim verification,
including semantic similarity matching and classification.
"""

from model.semantic_classifier import SemanticClassifier, get_semantic_classifier, SimilarityMatch

__all__ = [
    "SemanticClassifier",
    "get_semantic_classifier",
    "SimilarityMatch",
]
