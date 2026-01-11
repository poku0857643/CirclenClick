#!/usr/bin/env python3
"""
Test Cloud Fact-Checking APIs

This script tests the integration with external fact-checking APIs
to verify they're configured correctly and working.

Usage:
    python scripts/test_cloud_apis.py
    python scripts/test_cloud_apis.py --google-only
    python scripts/test_cloud_apis.py --claim "Custom claim to test"
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cloud.google_factcheck import GoogleFactCheckClient
from cloud.claimbuster import ClaimBusterClient
from cloud.factiverse import FactiverseClient
from utils.logger import get_logger
from utils.config import settings

logger = get_logger(__name__)


# Test claims covering different topics
TEST_CLAIMS = [
    "The Earth is flat",
    "Vaccines cause autism",
    "Climate change is caused by human activity",
    "The 2020 US election was stolen",
    "COVID-19 vaccines contain microchips"
]


async def test_google_api(claim: str):
    """Test Google Fact Check API"""
    print("\n🔍 Testing Google Fact Check API...")
    print("=" * 70)

    client = GoogleFactCheckClient()

    if not client.is_configured:
        print("❌ Google Fact Check API: NOT CONFIGURED")
        print("   To configure:")
        print("   1. Get API key from: https://console.cloud.google.com/")
        print("   2. Add to .env file: GOOGLE_FACTCHECK_API_KEY=your_key_here")
        print("   3. See docs/API_SETUP.md for detailed instructions")
        return False

    try:
        print(f"✅ API Key: Configured ({client.api_key[:8]}...{client.api_key[-4:]})")
        print(f"📝 Testing claim: \"{claim}\"")
        print()

        result = await client.verify_claim(claim)

        if result:
            print("✅ API Response: SUCCESS")
            print(f"   Rating: {result.rating.value}")
            print(f"   Confidence: {result.confidence}%")
            print(f"   Sources: {len(result.sources)} fact-checker(s)")
            if result.sources:
                print(f"   Top source: {result.sources[0].name}")
            print(f"   Explanation: {result.explanation[:100]}...")
            return True
        else:
            print("⚠️  API Response: No fact-checks found for this claim")
            print("   This is normal - not all claims have been fact-checked")
            print("   Try a more well-known claim or recent news headline")
            return True  # Still counts as working

    except Exception as e:
        print(f"❌ API Error: {e}")
        logger.error(f"Google API test failed: {e}", exc_info=True)
        return False


async def test_claimbuster_api(claim: str):
    """Test ClaimBuster API"""
    print("\n🔍 Testing ClaimBuster API...")
    print("=" * 70)

    client = ClaimBusterClient()

    if not client.is_configured:
        print("❌ ClaimBuster API: NOT CONFIGURED")
        print("   To configure:")
        print("   1. Register at: https://idir.uta.edu/claimbuster/")
        print("   2. Add to .env file: CLAIMBUSTER_API_KEY=your_key_here")
        print("   3. See docs/API_SETUP.md for detailed instructions")
        return False

    try:
        print(f"✅ API Key: Configured ({client.api_key[:8]}...{client.api_key[-4:]})")
        print(f"📝 Testing claim: \"{claim}\"")
        print()

        result = await client.verify_claim(claim)

        if result:
            print("✅ API Response: SUCCESS")
            print(f"   Rating: {result.rating.value}")
            print(f"   Confidence: {result.confidence}%")
            print(f"   Explanation: {result.explanation[:100]}...")
            return True
        else:
            print("⚠️  API Response: No results")
            return True  # Still counts as working

    except Exception as e:
        print(f"❌ API Error: {e}")
        logger.error(f"ClaimBuster API test failed: {e}", exc_info=True)
        return False


async def test_factiverse_api(claim: str):
    """Test Factiverse API"""
    print("\n🔍 Testing Factiverse API...")
    print("=" * 70)

    client = FactiverseClient()

    if not client.is_configured:
        print("❌ Factiverse API: NOT CONFIGURED")
        print("   To configure:")
        print("   1. Contact: https://www.factiverse.ai/")
        print("   2. Add to .env file: FACTIVERSE_API_KEY=your_key_here")
        print("   3. See docs/API_SETUP.md for detailed instructions")
        return False

    try:
        print(f"✅ API Key: Configured ({client.api_key[:8]}...{client.api_key[-4:]})")
        print(f"📝 Testing claim: \"{claim}\"")
        print()

        result = await client.verify_claim(claim)

        if result:
            print("✅ API Response: SUCCESS")
            print(f"   Rating: {result.rating.value}")
            print(f"   Confidence: {result.confidence}%")
            print(f"   Explanation: {result.explanation[:100]}...")
            return True
        else:
            print("⚠️  API Response: No results")
            return True  # Still counts as working

    except Exception as e:
        print(f"❌ API Error: {e}")
        logger.error(f"Factiverse API test failed: {e}", exc_info=True)
        return False


async def main():
    parser = argparse.ArgumentParser(description="Test cloud fact-checking APIs")
    parser.add_argument(
        "--claim",
        type=str,
        help="Specific claim to test (default: test multiple claims)"
    )
    parser.add_argument(
        "--google-only",
        action="store_true",
        help="Test only Google Fact Check API"
    )
    parser.add_argument(
        "--claimbuster-only",
        action="store_true",
        help="Test only ClaimBuster API"
    )
    parser.add_argument(
        "--factiverse-only",
        action="store_true",
        help="Test only Factiverse API"
    )

    args = parser.parse_args()

    # Select test claim
    test_claim = args.claim if args.claim else TEST_CLAIMS[0]

    print("=" * 70)
    print("  CLOUD API TESTING")
    print("=" * 70)
    print(f"Test Claim: \"{test_claim}\"")

    # Check environment
    if not settings.has_cloud_apis():
        print("\n⚠️  WARNING: No cloud APIs configured!")
        print("\nTo enable cloud fact-checking:")
        print("1. Copy .env.example to .env")
        print("2. Add your API keys")
        print("3. See docs/API_SETUP.md for instructions")
        print("\nContinuing with tests to show configuration status...\n")

    results = {}

    # Test APIs based on flags
    if args.google_only:
        results["Google"] = await test_google_api(test_claim)
    elif args.claimbuster_only:
        results["ClaimBuster"] = await test_claimbuster_api(test_claim)
    elif args.factiverse_only:
        results["Factiverse"] = await test_factiverse_api(test_claim)
    else:
        # Test all APIs
        results["Google"] = await test_google_api(test_claim)
        results["ClaimBuster"] = await test_claimbuster_api(test_claim)
        results["Factiverse"] = await test_factiverse_api(test_claim)

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)

    configured_count = sum(1 for success in results.values() if success is not False)
    working_count = sum(1 for success in results.values() if success is True)

    for api_name, success in results.items():
        status = "✅ WORKING" if success is True else ("⚠️  NOT CONFIGURED" if success is False else "❌ ERROR")
        print(f"{api_name:15} {status}")

    print()
    print(f"Configured APIs: {configured_count}/{len(results)}")
    print(f"Working APIs:    {working_count}/{len(results)}")

    if working_count == 0:
        print("\n❌ No cloud APIs are working!")
        print("   The system will use local database only.")
        print("   See docs/API_SETUP.md to configure APIs for broader coverage.")
        sys.exit(1)
    elif working_count < len(results):
        print(f"\n⚠️  {len(results) - working_count} API(s) not configured")
        print("   See docs/API_SETUP.md to enable more APIs")
        sys.exit(0)
    else:
        print("\n✅ All APIs working! Full cloud verification enabled.")
        sys.exit(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
