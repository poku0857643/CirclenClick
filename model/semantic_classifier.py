
"""
Semantic Classification Model for Claim Verification

Uses sentence transformers for semantic similarity matching and
claim classification without requiring external APIs.
"""

import os
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import json

from utils.logger import get_logger
from core.models import Verdict
from core.claims_database import ClaimsDatabase

logger = get_logger(__name__)


@dataclass
class SimilarityMatch:
    """Result of semantic similarity search"""
    claim: str
    similarity: float
    verdict: Verdict
    confidence: float
    explanation: str
    evidence: List[str]
    sources: List[str]


class SemanticClassifier:
    """
    Semantic classifier for claim verification

    Uses sentence embeddings to find similar claims in the database
    and classify new claims based on semantic similarity.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", use_transformers: bool = True):
        """
        Initialize semantic classifier

        Args:
            model_name: Name of the sentence transformer model
            use_transformers: Whether to use transformers (requires installation)
        """
        self.logger = logger
        self.model_name = model_name
        self.use_transformers = use_transformers
        self.model = None
        self.embeddings_cache: Dict[str, np.ndarray] = {}

        # Try to load the model
        self._load_model()

    def _load_model(self):
        """Load the sentence transformer model"""
        if not self.use_transformers:
            self.logger.info("Transformers disabled, using fallback matching")
            return

        try:
            from sentence_transformers import SentenceTransformer

            self.logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.logger.info("Model loaded successfully")

            # Pre-compute embeddings for database claims
            self._precompute_embeddings()

        except ImportError:
            self.logger.warning(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            self.use_transformers = False
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            self.use_transformers = False

    def _precompute_embeddings(self):
        """Pre-compute embeddings for all claims in the database"""
        if not self.model:
            return

        self.logger.info("Pre-computing embeddings for database claims...")

        all_claims = []

        # Get all claims from database
        for claim_dict in [
            ClaimsDatabase.FALSE_CLAIMS,
            ClaimsDatabase.TRUE_CLAIMS,
            ClaimsDatabase.MISLEADING_CLAIMS
        ]:
            all_claims.extend(claim_dict.keys())

        # Compute embeddings in batch (more efficient)
        embeddings = self.model.encode(all_claims, show_progress_bar=False)

        # Store in cache
        for claim, embedding in zip(all_claims, embeddings):
            self.embeddings_cache[claim] = embedding

        self.logger.info(f"Pre-computed {len(all_claims)} embeddings")

    def find_similar_claims(
        self,
        query: str,
        threshold: float = 0.7,
        top_k: int = 3
    ) -> List[SimilarityMatch]:
        """
        Find semantically similar claims in the database

        Args:
            query: Query claim to match
            threshold: Minimum similarity score (0-1)
            top_k: Number of top matches to return

        Returns:
            List of similar claims with similarity scores
        """
        if not self.model:
            # Fallback to string matching
            return self._fallback_matching(query, threshold)

        try:
            # Encode the query
            query_embedding = self.model.encode([query])[0]

            # Compute similarities with all cached embeddings
            similarities = []

            for db_claim, db_embedding in self.embeddings_cache.items():
                # Cosine similarity
                similarity = np.dot(query_embedding, db_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(db_embedding)
                )

                if similarity >= threshold:
                    # Find the claim data
                    claim_data = self._get_claim_data(db_claim)
                    if claim_data:
                        similarities.append(SimilarityMatch(
                            claim=db_claim,
                            similarity=float(similarity),
                            verdict=claim_data["verdict"],
                            confidence=claim_data["confidence"],
                            explanation=claim_data["explanation"],
                            evidence=claim_data["evidence"],
                            sources=claim_data["sources"]
                        ))

            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x.similarity, reverse=True)
            return similarities[:top_k]

        except Exception as e:
            self.logger.error(f"Error in semantic matching: {e}")
            return self._fallback_matching(query, threshold)

    def _get_claim_data(self, claim: str) -> Optional[Dict]:
        """Get claim data from database"""
        for db_dict in [
            ClaimsDatabase.FALSE_CLAIMS,
            ClaimsDatabase.TRUE_CLAIMS,
            ClaimsDatabase.MISLEADING_CLAIMS
        ]:
            if claim in db_dict:
                return db_dict[claim]
        return None

    def _fallback_matching(self, query: str, threshold: float) -> List[SimilarityMatch]:
        """
        Fallback matching using simple string similarity
        Used when transformers are not available
        """
        matches = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Search all dictionaries
        for db_dict in [
            ClaimsDatabase.FALSE_CLAIMS,
            ClaimsDatabase.TRUE_CLAIMS,
            ClaimsDatabase.MISLEADING_CLAIMS
        ]:
            for db_claim, claim_data in db_dict.items():
                db_words = set(db_claim.split())

                # Calculate word overlap similarity
                if not db_words:
                    continue

                intersection = len(query_words & db_words)
                union = len(query_words | db_words)
                similarity = intersection / union if union > 0 else 0.0

                # Also check if db_claim is substring of query or vice versa
                if db_claim in query_lower or query_lower in db_claim:
                    similarity = max(similarity, 0.85)

                if similarity >= threshold:
                    matches.append(SimilarityMatch(
                        claim=db_claim,
                        similarity=similarity,
                        verdict=claim_data["verdict"],
                        confidence=claim_data["confidence"],
                        explanation=claim_data["explanation"],
                        evidence=claim_data["evidence"],
                        sources=claim_data["sources"]
                    ))

        # Sort by similarity
        matches.sort(key=lambda x: x.similarity, reverse=True)
        return matches[:3]

    def classify_claim(self, claim: str) -> Optional[SimilarityMatch]:
        """
        Classify a claim by finding the most similar known claim

        Args:
            claim: Claim to classify

        Returns:
            Best matching claim with verdict, or None if no good match
        """
        similar_claims = self.find_similar_claims(claim, threshold=0.65, top_k=1)

        if similar_claims:
            best_match = similar_claims[0]

            # Adjust confidence based on similarity
            adjusted_confidence = best_match.confidence * best_match.similarity

            self.logger.info(
                f"Classified claim with {best_match.similarity:.2f} similarity: "
                f"{best_match.verdict.value} ({adjusted_confidence:.1f}% confidence)"
            )

            # Return match with adjusted confidence
            return SimilarityMatch(
                claim=best_match.claim,
                similarity=best_match.similarity,
                verdict=best_match.verdict,
                confidence=adjusted_confidence,
                explanation=best_match.explanation,
                evidence=best_match.evidence,
                sources=best_match.sources
            )

        return None

    def is_model_available(self) -> bool:
        """Check if the transformer model is available"""
        return self.model is not None

    def get_model_info(self) -> Dict[str, any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "transformers_available": self.use_transformers,
            "model_loaded": self.model is not None,
            "cached_embeddings": len(self.embeddings_cache),
            "fallback_mode": not self.is_model_available()
        }


# Global instance (lazy loaded)
_classifier: Optional[SemanticClassifier] = None


def get_semantic_classifier() -> SemanticClassifier:
    """Get or create the global semantic classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = SemanticClassifier()
    return _classifier
