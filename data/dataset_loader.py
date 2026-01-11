"""
Dataset Loader for Fact-Checking Databases

Downloads and processes public fact-checking datasets to expand
the claims database for better coverage.

Supported datasets:
- FEVER: 185K claims from Wikipedia fact verification
- LIAR: 12.8K claims from PolitiFact
- Custom datasets from cloud APIs
"""

import json
import os
from typing import List, Dict, Tuple
from pathlib import Path

from utils.logger import get_logger
from core.models import Verdict

logger = get_logger(__name__)


class DatasetLoader:
    """Load and process public fact-checking datasets"""

    def __init__(self, cache_dir: str = "data/cache"):
        """Initialize dataset loader

        Args:
            cache_dir: Directory to cache downloaded datasets
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger

    def load_fever_dataset(self, split: str = "train", max_samples: int = 10000) -> List[Dict]:
        """Load FEVER dataset from Hugging Face

        Args:
            split: Dataset split (train/validation/test)
            max_samples: Maximum number of samples to load

        Returns:
            List of claim dictionaries with verdict and evidence
        """
        try:
            from datasets import load_dataset

            self.logger.info(f"Loading FEVER dataset ({split} split, max {max_samples} samples)...")

            # Load dataset from Hugging Face
            dataset = load_dataset("fever", "v1.0", split=split, trust_remote_code=True)

            claims = []
            count = 0

            for item in dataset:
                if count >= max_samples:
                    break

                # Convert FEVER label to our verdict system
                label = item.get("label", "NOT ENOUGH INFO")
                if label == "SUPPORTS":
                    verdict = Verdict.TRUE
                    confidence = 85.0
                elif label == "REFUTES":
                    verdict = Verdict.FALSE
                    confidence = 85.0
                else:  # NOT ENOUGH INFO
                    verdict = Verdict.UNCERTAIN
                    confidence = 50.0

                # Extract claim and evidence
                claim_text = item.get("claim", "").strip()

                if not claim_text or len(claim_text) < 10:
                    continue

                # Build evidence from Wikipedia evidence sentences
                evidence_list = []
                evidence_items = item.get("evidence_annotation_id", [])
                if evidence_items:
                    evidence_list.append(f"Evidence from {len(evidence_items)} Wikipedia source(s)")

                claims.append({
                    "claim": claim_text,
                    "verdict": verdict,
                    "confidence": confidence,
                    "explanation": f"This claim was verified against Wikipedia evidence and found to be {verdict.value.lower()}.",
                    "evidence": evidence_list if evidence_list else ["Verified via Wikipedia fact-checking"],
                    "sources": ["FEVER Dataset", "Wikipedia"],
                    "dataset": "FEVER"
                })

                count += 1

            self.logger.info(f"Loaded {len(claims)} claims from FEVER dataset")
            return claims

        except ImportError:
            self.logger.error("Hugging Face datasets not installed. Run: pip install datasets")
            return []
        except Exception as e:
            self.logger.error(f"Error loading FEVER dataset: {e}")
            return []

    def load_liar_dataset(self, max_samples: int = 5000) -> List[Dict]:
        """Load LIAR dataset from Hugging Face

        Args:
            max_samples: Maximum number of samples to load

        Returns:
            List of claim dictionaries with verdict and evidence
        """
        try:
            from datasets import load_dataset

            self.logger.info(f"Loading LIAR dataset (max {max_samples} samples)...")

            # Load dataset from Hugging Face
            dataset = load_dataset("ucsbnlp/liar", split="train", trust_remote_code=True)

            claims = []
            count = 0

            for item in dataset:
                if count >= max_samples:
                    break

                # Convert LIAR label to our verdict system
                label = item.get("label", -1)

                # LIAR labels: 0=pants-fire, 1=false, 2=barely-true, 3=half-true, 4=mostly-true, 5=true
                if label in [5, 4]:  # true, mostly-true
                    verdict = Verdict.TRUE
                    confidence = 80.0 if label == 5 else 70.0
                elif label in [0, 1]:  # pants-fire, false
                    verdict = Verdict.FALSE
                    confidence = 90.0 if label == 0 else 85.0
                elif label in [2, 3]:  # barely-true, half-true
                    verdict = Verdict.MISLEADING
                    confidence = 70.0
                else:
                    continue  # Skip unknown labels

                # Extract claim
                claim_text = item.get("statement", "").strip()

                if not claim_text or len(claim_text) < 10:
                    continue

                # Build evidence
                subject = item.get("subject", "")
                speaker = item.get("speaker", "")
                context = item.get("context", "")

                evidence_list = []
                if speaker:
                    evidence_list.append(f"Statement by {speaker}")
                if subject:
                    evidence_list.append(f"Subject: {subject}")
                if context:
                    evidence_list.append(f"Context: {context[:100]}")

                label_text = ["pants-fire", "false", "barely-true", "half-true", "mostly-true", "true"][label]

                claims.append({
                    "claim": claim_text,
                    "verdict": verdict,
                    "confidence": confidence,
                    "explanation": f"This claim was fact-checked by PolitiFact and rated as '{label_text}'.",
                    "evidence": evidence_list if evidence_list else ["Verified via PolitiFact"],
                    "sources": ["LIAR Dataset", "PolitiFact"],
                    "dataset": "LIAR"
                })

                count += 1

            self.logger.info(f"Loaded {len(claims)} claims from LIAR dataset")
            return claims

        except ImportError:
            self.logger.error("Hugging Face datasets not installed. Run: pip install datasets")
            return []
        except Exception as e:
            self.logger.error(f"Error loading LIAR dataset: {e}")
            return []

    def save_claims_to_file(self, claims: List[Dict], filename: str):
        """Save claims to JSON file for caching

        Args:
            claims: List of claim dictionaries
            filename: Output filename
        """
        output_path = self.cache_dir / filename

        # Convert Verdict enums to strings for JSON serialization
        claims_json = []
        for claim in claims:
            claim_copy = claim.copy()
            claim_copy["verdict"] = claim["verdict"].value
            claims_json.append(claim_copy)

        with open(output_path, "w") as f:
            json.dump(claims_json, f, indent=2)

        self.logger.info(f"Saved {len(claims)} claims to {output_path}")

    def load_claims_from_file(self, filename: str) -> List[Dict]:
        """Load claims from cached JSON file

        Args:
            filename: Input filename

        Returns:
            List of claim dictionaries
        """
        file_path = self.cache_dir / filename

        if not file_path.exists():
            self.logger.warning(f"Cache file not found: {file_path}")
            return []

        with open(file_path, "r") as f:
            claims_json = json.load(f)

        # Convert verdict strings back to Verdict enums
        claims = []
        for claim in claims_json:
            claim_copy = claim.copy()
            claim_copy["verdict"] = Verdict(claim["verdict"])
            claims.append(claim_copy)

        self.logger.info(f"Loaded {len(claims)} claims from {file_path}")
        return claims

    def get_combined_dataset(self,
                            fever_samples: int = 10000,
                            liar_samples: int = 5000,
                            use_cache: bool = True) -> List[Dict]:
        """Get combined dataset from all sources

        Args:
            fever_samples: Number of FEVER samples to load
            liar_samples: Number of LIAR samples to load
            use_cache: Whether to use cached datasets

        Returns:
            Combined list of claims from all datasets
        """
        cache_file = f"combined_dataset_{fever_samples}_{liar_samples}.json"

        # Try loading from cache first
        if use_cache:
            cached_claims = self.load_claims_from_file(cache_file)
            if cached_claims:
                return cached_claims

        # Load fresh datasets
        self.logger.info("Loading fresh datasets from sources...")

        all_claims = []

        # Load FEVER
        fever_claims = self.load_fever_dataset(split="train", max_samples=fever_samples)
        all_claims.extend(fever_claims)

        # Load LIAR
        liar_claims = self.load_liar_dataset(max_samples=liar_samples)
        all_claims.extend(liar_claims)

        # Save to cache
        self.save_claims_to_file(all_claims, cache_file)

        self.logger.info(f"Combined dataset: {len(all_claims)} total claims")
        return all_claims


# Global instance
_loader = None

def get_dataset_loader() -> DatasetLoader:
    """Get or create global dataset loader instance"""
    global _loader
    if _loader is None:
        _loader = DatasetLoader()
    return _loader
