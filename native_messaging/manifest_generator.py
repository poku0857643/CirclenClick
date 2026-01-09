"""Generate native messaging manifests for Chrome and Firefox."""

import json
import platform
import sys
from pathlib import Path
from typing import Dict, Any

from utils.logger import get_logger

logger = get_logger(__name__)


class ManifestGenerator:
    """Generates native messaging manifest files for different browsers."""

    # Extension ID for Chrome (must match manifest.json)
    CHROME_EXTENSION_ID = "circlenclick@extension.id"

    # Extension ID for Firefox (must match manifest.json)
    FIREFOX_EXTENSION_ID = "circlenclick@anthropic.com"

    def __init__(self, project_root: Path):
        """Initialize manifest generator.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.host_script = project_root / "native_messaging" / "host.py"
        self.logger = logger

    def generate_chrome_manifest(self) -> Dict[str, Any]:
        """Generate Chrome native messaging manifest.

        Returns:
            Manifest dictionary
        """
        # Get Python interpreter path
        python_path = sys.executable

        manifest = {
            "name": "com.anthropic.circlenclick",
            "description": "CircleNClick content verification host",
            "path": str(self.host_script.absolute()),
            "type": "stdio",
            "allowed_origins": [
                f"chrome-extension://{self.CHROME_EXTENSION_ID}/"
            ]
        }

        return manifest

    def generate_firefox_manifest(self) -> Dict[str, Any]:
        """Generate Firefox native messaging manifest.

        Returns:
            Manifest dictionary
        """
        manifest = {
            "name": "com.anthropic.circlenclick",
            "description": "CircleNClick content verification host",
            "path": str(self.host_script.absolute()),
            "type": "stdio",
            "allowed_extensions": [
                self.FIREFOX_EXTENSION_ID
            ]
        }

        return manifest

    def get_chrome_manifest_path(self) -> Path:
        """Get the Chrome native messaging manifest install path.

        Returns:
            Path where Chrome looks for manifests
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "NativeMessagingHosts"
        elif system == "Linux":
            return Path.home() / ".config" / "google-chrome" / "NativeMessagingHosts"
        elif system == "Windows":
            # Windows uses registry, but we'll return a path anyway
            return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "NativeMessagingHosts"
        else:
            raise OSError(f"Unsupported platform: {system}")

    def get_firefox_manifest_path(self) -> Path:
        """Get the Firefox native messaging manifest install path.

        Returns:
            Path where Firefox looks for manifests
        """
        system = platform.system()

        if system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Mozilla" / "NativeMessagingHosts"
        elif system == "Linux":
            return Path.home() / ".mozilla" / "native-messaging-hosts"
        elif system == "Windows":
            # Windows uses registry
            return Path.home() / "AppData" / "Roaming" / "Mozilla" / "NativeMessagingHosts"
        else:
            raise OSError(f"Unsupported platform: {system}")

    def write_manifest(self, manifest: Dict[str, Any], path: Path, manifest_name: str = "com.anthropic.circlenclick.json"):
        """Write manifest to file.

        Args:
            manifest: Manifest dictionary
            path: Directory to write manifest to
            manifest_name: Name of manifest file
        """
        # Create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)

        # Write manifest
        manifest_file = path / manifest_name
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)

        self.logger.info(f"Wrote manifest to {manifest_file}")

        # Make host script executable on Unix-like systems
        if platform.system() != "Windows":
            import os
            import stat
            os.chmod(self.host_script, os.stat(self.host_script).st_mode | stat.S_IEXEC)
            self.logger.info(f"Made {self.host_script} executable")

    def install_chrome_manifest(self):
        """Install Chrome native messaging manifest."""
        manifest = self.generate_chrome_manifest()
        path = self.get_chrome_manifest_path()
        self.write_manifest(manifest, path)
        self.logger.info(f"Installed Chrome manifest to {path}")

    def install_firefox_manifest(self):
        """Install Firefox native messaging manifest."""
        manifest = self.generate_firefox_manifest()
        path = self.get_firefox_manifest_path()
        self.write_manifest(manifest, path)
        self.logger.info(f"Installed Firefox manifest to {path}")

    def install_all(self):
        """Install manifests for all supported browsers."""
        try:
            self.install_chrome_manifest()
        except Exception as e:
            self.logger.error(f"Failed to install Chrome manifest: {e}")

        try:
            self.install_firefox_manifest()
        except Exception as e:
            self.logger.error(f"Failed to install Firefox manifest: {e}")
