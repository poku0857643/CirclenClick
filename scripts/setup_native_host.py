#!/usr/bin/env python3
"""Setup script for native messaging host installation."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from native_messaging.manifest_generator import ManifestGenerator
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    """Main setup function."""
    console.print("\n[bold cyan]CircleNClick Native Messaging Host Setup[/bold cyan]\n")

    # Get project root
    project_root = Path(__file__).parent.parent
    console.print(f"Project root: [dim]{project_root}[/dim]")

    # Create manifest generator
    generator = ManifestGenerator(project_root)

    # Install manifests
    console.print("\n[yellow]Installing native messaging manifests...[/yellow]\n")

    try:
        # Chrome
        console.print("📦 Installing Chrome manifest...")
        generator.install_chrome_manifest()
        chrome_path = generator.get_chrome_manifest_path()
        console.print(f"   ✓ Installed to: [dim]{chrome_path}[/dim]")

        # Firefox
        console.print("\n📦 Installing Firefox manifest...")
        generator.install_firefox_manifest()
        firefox_path = generator.get_firefox_manifest_path()
        console.print(f"   ✓ Installed to: [dim]{firefox_path}[/dim]")

        console.print("\n[bold green]✓ Installation complete![/bold green]\n")

        # Show next steps
        console.print(Panel(
            "[bold]Next Steps:[/bold]\n\n"
            "1. Build the browser extension:\n"
            "   [dim]cd extension && npm install && npm run build[/dim]\n\n"
            "2. Load extension in browser:\n"
            "   [bold cyan]Chrome:[/bold cyan] chrome://extensions → Developer mode → Load unpacked → extension/dist\n"
            "   [bold cyan]Firefox:[/bold cyan] about:debugging → Load Temporary Add-on\n\n"
            "3. Test the extension on a social media platform\n\n"
            "4. Check logs:\n"
            "   [dim]tail -f logs/native_host.log[/dim]",
            title="Setup Complete",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[bold red]✗ Installation failed:[/bold red] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
