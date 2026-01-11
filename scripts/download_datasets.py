#!/usr/bin/env python3
"""
Download and cache public fact-checking datasets

This script downloads FEVER and LIAR datasets from Hugging Face
and caches them locally for use by the semantic classifier.

Usage:
    python scripts/download_datasets.py --fever 10000 --liar 5000
    python scripts/download_datasets.py --quick  # Download 1000 samples each
    python scripts/download_datasets.py --full   # Download full datasets
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.dataset_loader import get_dataset_loader
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Download fact-checking datasets")
    parser.add_argument(
        "--fever",
        type=int,
        default=1000,
        help="Number of FEVER samples to download (default: 1000)"
    )
    parser.add_argument(
        "--liar",
        type=int,
        default=1000,
        help="Number of LIAR samples to download (default: 1000)"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: Download 1000 samples from each dataset"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full mode: Download all available samples (may take time)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignore cache and download fresh datasets"
    )

    args = parser.parse_args()

    # Set sample counts based on mode
    if args.quick:
        fever_samples = 1000
        liar_samples = 1000
    elif args.full:
        fever_samples = 100000  # Download up to 100K from FEVER
        liar_samples = 12000    # Full LIAR dataset
    else:
        fever_samples = args.fever
        liar_samples = args.liar

    print("=" * 70)
    print("  DOWNLOADING FACT-CHECKING DATASETS")
    print("=" * 70)
    print(f"FEVER samples: {fever_samples}")
    print(f"LIAR samples:  {liar_samples}")
    print(f"Use cache:     {not args.no_cache}")
    print("=" * 70)
    print()

    # Load datasets
    loader = get_dataset_loader()

    try:
        claims = loader.get_combined_dataset(
            fever_samples=fever_samples,
            liar_samples=liar_samples,
            use_cache=not args.no_cache
        )

        print()
        print("=" * 70)
        print("  DOWNLOAD COMPLETE")
        print("=" * 70)
        print(f"Total claims loaded: {len(claims)}")
        print()

        # Show statistics
        from core.models import Verdict

        verdict_counts = {
            Verdict.TRUE: 0,
            Verdict.FALSE: 0,
            Verdict.MISLEADING: 0,
            Verdict.UNCERTAIN: 0
        }

        dataset_counts = {}

        for claim in claims:
            verdict_counts[claim["verdict"]] += 1
            dataset = claim.get("dataset", "Unknown")
            dataset_counts[dataset] = dataset_counts.get(dataset, 0) + 1

        print("Verdict Distribution:")
        print(f"  ✅ TRUE:       {verdict_counts[Verdict.TRUE]:>6} ({verdict_counts[Verdict.TRUE]/len(claims)*100:.1f}%)")
        print(f"  ❌ FALSE:      {verdict_counts[Verdict.FALSE]:>6} ({verdict_counts[Verdict.FALSE]/len(claims)*100:.1f}%)")
        print(f"  ⚠️  MISLEADING: {verdict_counts[Verdict.MISLEADING]:>6} ({verdict_counts[Verdict.MISLEADING]/len(claims)*100:.1f}%)")
        print(f"  ❔ UNCERTAIN:  {verdict_counts[Verdict.UNCERTAIN]:>6} ({verdict_counts[Verdict.UNCERTAIN]/len(claims)*100:.1f}%)")
        print()

        print("Dataset Sources:")
        for dataset, count in dataset_counts.items():
            print(f"  {dataset}: {count} claims")
        print()

        # Show sample claims
        print("Sample Claims:")
        print("-" * 70)
        for i, claim in enumerate(claims[:3], 1):
            print(f"\n{i}. {claim['verdict'].value}: {claim['claim'][:100]}...")
            print(f"   Confidence: {claim['confidence']}%")
            print(f"   Source: {claim.get('dataset', 'Unknown')}")

        print()
        print("=" * 70)
        print(f"✅ Datasets cached in: {loader.cache_dir}")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Failed to download datasets: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have installed: pip install datasets")
        sys.exit(1)


if __name__ == "__main__":
    main()
