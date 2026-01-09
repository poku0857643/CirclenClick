#!/usr/bin/env python3
"""
CircleNClick CLI - Command-line interface for testing content verification.

Usage:
    python cli.py verify "Content to verify"
    python cli.py verify --file path/to/file.txt
    python cli.py verify --url https://twitter.com/user/status/123
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from core.verification_engine import VerificationEngine
from core.models import Verdict
from core.hybrid_decisor import VerificationStrategy
from utils.config import settings
from utils.logger import logger

console = Console()


def print_banner():
    """Print CLI banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║      CircleNClick Content Verifier       ║
    ║   Check if content is fake, AI-generated,║
    ║         or contains misinformation       ║
    ╚═══════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def get_verdict_color(verdict: Verdict) -> str:
    """Get color for verdict display."""
    colors = {
        Verdict.TRUE: "green",
        Verdict.FALSE: "red",
        Verdict.MISLEADING: "yellow",
        Verdict.UNVERIFIABLE: "bright_black",
        Verdict.UNCERTAIN: "bright_black"
    }
    return colors.get(verdict, "white")


def get_verdict_emoji(verdict: Verdict) -> str:
    """Get emoji for verdict."""
    emojis = {
        Verdict.TRUE: "✓",
        Verdict.FALSE: "✗",
        Verdict.MISLEADING: "⚠",
        Verdict.UNVERIFIABLE: "?",
        Verdict.UNCERTAIN: "?"
    }
    return emojis.get(verdict, "?")


def display_result(result):
    """Display verification result in a nice format."""
    # Verdict panel
    verdict_color = get_verdict_color(result.verdict)
    verdict_emoji = get_verdict_emoji(result.verdict)

    verdict_text = f"{verdict_emoji} {result.verdict.value}"
    console.print()
    console.print(Panel(
        verdict_text,
        title="Verdict",
        style=f"bold {verdict_color}",
        border_style=verdict_color
    ))

    # Details table
    table = Table(box=box.ROUNDED, show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Confidence", f"{result.confidence:.1f}%")
    table.add_row("Strategy Used", result.strategy_used.value)
    table.add_row("Processing Time", f"{result.processing_time:.2f}s")

    console.print(table)

    # Explanation
    console.print()
    console.print(Panel(
        result.explanation,
        title="Explanation",
        style="white"
    ))

    # Evidence
    if result.evidence:
        console.print()
        console.print("[bold]Evidence:[/bold]")
        for i, evidence in enumerate(result.evidence, 1):
            console.print(f"  {i}. {evidence}")

    # Sources
    if result.sources:
        console.print()
        console.print("[bold]Sources:[/bold]")
        for i, source in enumerate(result.sources, 1):
            console.print(f"  {i}. {source}")

    console.print()


@click.group()
def cli():
    """CircleNClick - Content verification tool."""
    pass


@cli.command()
@click.argument('text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Read content from file')
@click.option('--url', '-u', help='URL of the content')
@click.option('--platform', '-p', type=click.Choice(['facebook', 'twitter', 'threads']), help='Social media platform')
@click.option('--strategy', '-s', type=click.Choice(['local', 'cloud', 'hybrid']), default='hybrid', help='Verification strategy')
@click.option('--json', 'output_json', is_flag=True, help='Output result as JSON')
def verify(text: Optional[str], file: Optional[str], url: Optional[str], platform: Optional[str], strategy: str, output_json: bool):
    """Verify content for misinformation.

    Examples:
        python cli.py verify "The Earth is flat"
        python cli.py verify --file article.txt
        python cli.py verify "Some claim" --strategy local
    """
    if not output_json:
        print_banner()

    # Get content from text, file, or prompt
    if file:
        content = Path(file).read_text(encoding='utf-8')
        if not output_json:
            console.print(f"[dim]Reading from file: {file}[/dim]")
    elif text:
        content = text
    else:
        console.print("[yellow]No content provided. Enter content to verify (Ctrl+D when done):[/yellow]")
        content = sys.stdin.read().strip()

    if not content:
        console.print("[red]Error: No content to verify[/red]")
        sys.exit(1)

    # Map strategy string to enum
    strategy_map = {
        'local': VerificationStrategy.LOCAL_ONLY,
        'cloud': VerificationStrategy.CLOUD_ONLY,
        'hybrid': VerificationStrategy.HYBRID
    }
    verification_strategy = strategy_map[strategy]

    # Run verification
    if not output_json:
        with console.status("[bold green]Verifying content...", spinner="dots"):
            result = asyncio.run(run_verification(content, url, platform, verification_strategy))
    else:
        result = asyncio.run(run_verification(content, url, platform, verification_strategy))

    # Display result
    if output_json:
        import json
        console.print(json.dumps(result.to_dict(), indent=2))
    else:
        display_result(result)


async def run_verification(text: str, url: Optional[str], platform: Optional[str], strategy: VerificationStrategy):
    """Run async verification."""
    engine = VerificationEngine()
    result = await engine.verify(
        text=text,
        url=url,
        platform=platform,
        user_preference=strategy
    )
    return result


@cli.command()
def info():
    """Display system information and configuration."""
    console.print("[bold]CircleNClick Configuration[/bold]\n")

    table = Table(box=box.ROUNDED)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    table.add_column("Status", style="green")

    # API Keys
    api_keys = [
        ("Google Fact Check", settings.google_factcheck_api_key),
        ("ClaimBuster", settings.claimbuster_api_key),
        ("Factiverse", settings.factiverse_api_key),
        ("OpenAI", settings.openai_api_key),
        ("Anthropic", settings.anthropic_api_key)
    ]

    for name, key in api_keys:
        status = "✓ Configured" if key else "✗ Not configured"
        value = "***" if key else "Not set"
        table.add_row(f"{name} API", value, status)

    table.add_row("", "", "")  # Separator
    table.add_row("Redis", settings.redis_url, "✓ Enabled" if settings.redis_enabled else "✗ Disabled")
    table.add_row("Local Only Mode", str(settings.local_only_mode), "")
    table.add_row("Confidence Threshold", f"{settings.model_confidence_threshold}", "")
    table.add_row("Cache TTL", f"{settings.cache_ttl_hours}h", "")

    console.print(table)

    # Warnings
    if not settings.has_cloud_apis():
        console.print("\n[yellow]Warning: No cloud API keys configured. Only local verification will be available.[/yellow]")
        console.print("[dim]To enable cloud verification, configure API keys in .env file[/dim]")


@cli.command()
def test():
    """Run a quick test with sample content."""
    print_banner()

    test_cases = [
        ("The Earth is flat", "Should detect as FALSE"),
        ("I think pizza is delicious", "Should detect as opinion/unverifiable"),
        ("The company reported 50% growth in Q4 2024", "Should detect as factual claim")
    ]

    console.print("[bold]Running test cases...[/bold]\n")

    for text, description in test_cases:
        console.print(f"[cyan]Test:[/cyan] {text}")
        console.print(f"[dim]Expected: {description}[/dim]")

        result = asyncio.run(run_verification(text, None, None, VerificationStrategy.LOCAL_ONLY))

        console.print(f"[bold]Result:[/bold] {result.verdict.value} ({result.confidence:.1f}% confidence)")
        console.print()


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        logger.error(f"CLI error: {e}", exc_info=True)
        sys.exit(1)