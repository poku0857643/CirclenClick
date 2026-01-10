#!/usr/bin/env python3
"""
Update Chrome native messaging manifest with extension ID

Usage:
    python scripts/update_extension_id.py EXTENSION_ID

Example:
    python scripts/update_extension_id.py abcdefghijklmnopqrstuvwxyz123456
"""

import json
import sys
import os
from pathlib import Path

def update_chrome_manifest(extension_id: str):
    """Update Chrome native messaging manifest with extension ID"""

    # Validate extension ID format
    if len(extension_id) != 32 or not extension_id.isalnum():
        print("❌ Invalid extension ID format")
        print("Expected: 32 alphanumeric characters")
        print(f"Got: {extension_id} ({len(extension_id)} characters)")
        return False

    # Find Chrome manifest
    home = Path.home()
    manifest_path = home / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts" / "com.anthropic.circlenclick.json"

    if not manifest_path.exists():
        print(f"❌ Chrome manifest not found at: {manifest_path}")
        print("Run: python scripts/setup_native_host.py")
        return False

    # Update manifest
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        old_origins = manifest.get('allowed_origins', [])
        new_origin = f"chrome-extension://{extension_id}/"
        manifest['allowed_origins'] = [new_origin]

        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"✅ Updated Chrome manifest")
        print(f"   Old: {old_origins}")
        print(f"   New: {[new_origin]}")
        print()
        print("Next steps:")
        print("1. Go to chrome://extensions/")
        print("2. Click reload icon on CircleNClick extension")
        print("3. Test the extension!")

        return True

    except Exception as e:
        print(f"❌ Error updating manifest: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/update_extension_id.py EXTENSION_ID")
        print()
        print("To find your extension ID:")
        print("1. Open Chrome and go to chrome://extensions/")
        print("2. Find the CircleNClick extension")
        print("3. Look for 'ID:' under the extension name")
        print("4. Copy the 32-character ID")
        print()
        print("Example:")
        print("  python scripts/update_extension_id.py abcdefghijklmnopqrstuvwxyz123456")
        sys.exit(1)

    extension_id = sys.argv[1].strip()
    success = update_chrome_manifest(extension_id)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
