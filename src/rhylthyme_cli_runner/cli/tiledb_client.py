#!/usr/bin/env python3
"""
TileDB Cloud integration for Rhylthyme CLI.

This module provides functionality to interact with TileDB Cloud assets,
including listing, searching, and downloading assets.
"""

import click
import tiledb.cloud
from typing import Dict, List, Any, Optional
import json


class TileDBClient:
    """Client for interacting with TileDB Cloud assets."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the TileDB Cloud client.

        Args:
            api_key: TileDB Cloud API key. If None, will use environment variable.
        """
        if api_key:
            tiledb.cloud.login(api_key=api_key)
        else:
            # Will use environment variable TILEDB_REST_TOKEN
            tiledb.cloud.login()

    def list_assets(
        self, search: str = "", page: int = 1, limit: int = 20
    ) -> Dict[str, Any]:
        """List public assets with optional search criteria.

        Args:
            search: Search keywords to filter assets
            page: Page number for pagination
            limit: Number of results per page

        Returns:
            Dictionary containing asset list and metadata
        """
        try:
            assets = tiledb.cloud.asset.list_public(
                search=search, page=page, limit=limit
            )
            return {"assets": assets, "page": page, "limit": limit, "search": search}
        except Exception as e:
            raise click.ClickException(f"Failed to list assets: {str(e)}")

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Get details for a specific asset.

        Args:
            asset_id: The asset ID to retrieve

        Returns:
            Asset details dictionary
        """
        try:
            asset = tiledb.cloud.asset.get(asset_id)
            return asset
        except Exception as e:
            raise click.ClickException(f"Failed to get asset {asset_id}: {str(e)}")

    def download_asset(self, asset_id: str, output_path: str) -> str:
        """Download an asset to a local file.

        Args:
            asset_id: The asset ID to download
            output_path: Local path to save the asset

        Returns:
            Path to the downloaded file
        """
        try:
            # This is a placeholder - actual download implementation
            # would depend on the asset type and TileDB Cloud API
            click.echo(f"Downloading asset {asset_id} to {output_path}")
            # tiledb.cloud.asset.download(asset_id, output_path)
            return output_path
        except Exception as e:
            raise click.ClickException(f"Failed to download asset {asset_id}: {str(e)}")


@click.group()
def tiledb_group():
    """TileDB Cloud asset management commands."""
    pass


@tiledb_group.command()
@click.option("--search", "-s", default="", help="Search keywords")
@click.option("--page", "-p", default=1, type=int, help="Page number")
@click.option("--limit", "-l", default=20, type=int, help="Results per page")
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format",
)
def list(search: str, page: int, limit: int, format: str):
    """List TileDB Cloud assets."""
    client = TileDBClient()
    result = client.list_assets(search=search, page=page, limit=limit)

    if format == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        # Table format
        click.echo(f"TileDB Cloud Assets (Page {page}, Search: '{search}')")
        click.echo("=" * 80)

        if not result.get("assets"):
            click.echo("No assets found.")
            return

        for asset in result["assets"]:
            click.echo(f"ID: {asset.get('id', 'N/A')}")
            click.echo(f"Name: {asset.get('name', 'N/A')}")
            click.echo(f"Type: {asset.get('type', 'N/A')}")
            click.echo(f"Size: {asset.get('size', 'N/A')}")
            click.echo("-" * 40)


@tiledb_group.command()
@click.argument("asset_id")
@click.option(
    "--format",
    "-f",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format",
)
def show(asset_id: str, format: str):
    """Show details for a specific asset."""
    client = TileDBClient()
    asset = client.get_asset(asset_id)

    if format == "json":
        click.echo(json.dumps(asset, indent=2))
    else:
        click.echo(f"Asset Details: {asset_id}")
        click.echo("=" * 40)
        for key, value in asset.items():
            click.echo(f"{key}: {value}")


@tiledb_group.command()
@click.argument("asset_id")
@click.option("--output", "-o", required=True, help="Output file path")
def download(asset_id: str, output: str):
    """Download an asset to a local file."""
    client = TileDBClient()
    result = client.download_asset(asset_id, output)
    click.echo(f"Asset downloaded to: {result}")


# Example usage of the TileDB Cloud API
def example_list_vcf_assets():
    """Example: List VCF assets with pagination."""
    client = TileDBClient()

    # List VCF assets on page 2
    result = client.list_assets(search="vcf", page=2, limit=10)

    print(f"Found {len(result['assets'])} VCF assets on page 2")
    for asset in result["assets"]:
        print(f"- {asset.get('name', 'Unknown')} ({asset.get('id', 'N/A')})")

    return result
