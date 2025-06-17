#!/usr/bin/env python3
"""
Resource Specification CLI

Command-line interface for managing detailed resource specifications,
including adding photos, documents, and creating environments.
"""

import argparse
import json
import sys
import os
from typing import Optional, List
from datetime import datetime

# Handle imports for both module and script execution
try:
    from .resource_specs import ResourceSpecManager, ResourceSpecification, create_bakery_resources, create_sample_environment_with_resources
except ImportError:
    # If running as script, adjust path and use absolute imports
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from rhylthyme.resource_specs import ResourceSpecManager, ResourceSpecification, create_bakery_resources, create_sample_environment_with_resources


def create_resource_command(args):
    """Create a new resource specification."""
    manager = ResourceSpecManager(args.base_path)
    
    # Parse capacity from command line
    capacity = {}
    if args.capacity:
        for cap_spec in args.capacity:
            if '=' in cap_spec:
                key, value = cap_spec.split('=', 1)
                # Try to convert to number if possible
                try:
                    capacity[key] = float(value)
                except ValueError:
                    capacity[key] = value
    
    # Create the resource specification
    spec = manager.create_resource_spec(
        name=args.name,
        category=args.category,
        manufacturer=args.manufacturer,
        model=args.model,
        capacity=capacity,
        description=args.description or "",
        serial_number=args.serial_number,
        year_manufactured=args.year_manufactured
    )
    
    # Save the specification
    file_path = manager.save_resource_spec(spec)
    print(f"Created resource specification: {spec.resource_id}")
    print(f"Saved to: {file_path}")
    
    return spec.resource_id


def add_photo_command(args):
    """Add a photo to a resource specification."""
    manager = ResourceSpecManager(args.base_path)
    
    if not os.path.exists(args.photo_path):
        print(f"Error: Photo file not found: {args.photo_path}")
        return False
    
    try:
        photo_id = manager.add_photo(
            resource_id=args.resource_id,
            photo_path=args.photo_path,
            description=args.description or "",
            photo_type=args.photo_type
        )
        print(f"Added photo {photo_id} to resource {args.resource_id}")
        return True
    except ValueError as e:
        print(f"Error: {e}")
        return False


def add_document_command(args):
    """Add a document to a resource specification."""
    manager = ResourceSpecManager(args.base_path)
    
    if not os.path.exists(args.doc_path):
        print(f"Error: Document file not found: {args.doc_path}")
        return False
    
    try:
        doc_id = manager.add_document(
            resource_id=args.resource_id,
            doc_path=args.doc_path,
            doc_type=args.doc_type,
            description=args.description or ""
        )
        print(f"Added document {doc_id} to resource {args.resource_id}")
        return True
    except ValueError as e:
        print(f"Error: {e}")
        return False


def list_resources_command(args):
    """List all resource specifications."""
    manager = ResourceSpecManager(args.base_path)
    
    resources = manager.list_resources(category=args.category)
    
    if not resources:
        print("No resources found.")
        return
    
    print(f"Found {len(resources)} resource(s):")
    print("-" * 80)
    
    for spec in resources:
        print(f"ID: {spec.resource_id}")
        print(f"Name: {spec.name}")
        print(f"Category: {spec.category}")
        print(f"Manufacturer: {spec.manufacturer}")
        print(f"Model: {spec.model}")
        if spec.capacity:
            capacity_str = ", ".join([f"{k}: {v}" for k, v in spec.capacity.items()])
            print(f"Capacity: {capacity_str}")
        print(f"Photos: {len(spec.photos)}")
        print(f"Documents: {len(spec.manuals)}")
        print(f"Condition: {spec.condition}")
        print("-" * 80)


def show_resource_command(args):
    """Show detailed information about a specific resource."""
    manager = ResourceSpecManager(args.base_path)
    
    spec = manager.load_resource_spec(args.resource_id)
    if not spec:
        print(f"Resource {args.resource_id} not found.")
        return
    
    print(f"Resource Specification: {spec.resource_id}")
    print("=" * 60)
    print(f"Name: {spec.name}")
    print(f"Category: {spec.category}")
    print(f"Manufacturer: {spec.manufacturer}")
    print(f"Model: {spec.model}")
    
    if spec.serial_number:
        print(f"Serial Number: {spec.serial_number}")
    if spec.year_manufactured:
        print(f"Year Manufactured: {spec.year_manufactured}")
    
    print(f"\nCapacity:")
    for key, value in spec.capacity.items():
        print(f"  {key}: {value}")
    
    if spec.dimensions:
        print(f"\nDimensions:")
        for key, value in spec.dimensions.items():
            print(f"  {key}: {value}")
    
    if spec.power_requirements:
        print(f"\nPower Requirements:")
        for key, value in spec.power_requirements.items():
            print(f"  {key}: {value}")
    
    if spec.qualified_actor_types:
        print(f"\nQualified Actor Types:")
        for actor_type in spec.qualified_actor_types:
            print(f"  - {actor_type}")
    
    if spec.safety_requirements:
        print(f"\nSafety Requirements:")
        for requirement in spec.safety_requirements:
            print(f"  - {requirement}")
    
    if spec.photos:
        print(f"\nPhotos ({len(spec.photos)}):")
        for photo in spec.photos:
            print(f"  - {photo['photo_id']}: {photo['description']} ({photo['photo_type']})")
    
    if spec.manuals:
        print(f"\nDocuments ({len(spec.manuals)}):")
        for doc in spec.manuals:
            print(f"  - {doc['doc_id']}: {doc['description']} ({doc['doc_type']})")
    
    print(f"\nCondition: {spec.condition}")
    if spec.purchase_date:
        print(f"Purchase Date: {spec.purchase_date}")
    if spec.purchase_price:
        print(f"Purchase Price: ${spec.purchase_price:,.2f}")


def search_resources_command(args):
    """Search resources by query."""
    manager = ResourceSpecManager(args.base_path)
    
    fields = args.fields.split(',') if args.fields else None
    results = manager.search_resources(args.query, fields)
    
    if not results:
        print(f"No resources found matching '{args.query}'")
        return
    
    print(f"Found {len(results)} resource(s) matching '{args.query}':")
    print("-" * 60)
    
    for spec in results:
        print(f"{spec.resource_id}: {spec.name} ({spec.manufacturer} {spec.model})")


def export_catalog_command(args):
    """Export complete resource catalog."""
    manager = ResourceSpecManager(args.base_path)
    
    manager.export_resource_catalog(args.output_file)
    print(f"Exported resource catalog to: {args.output_file}")


def create_examples_command(args):
    """Create example bakery resources."""
    manager = ResourceSpecManager(args.base_path)
    
    resources = create_bakery_resources()
    
    print("Creating example bakery resources...")
    for key, spec in resources.items():
        file_path = manager.save_resource_spec(spec)
        print(f"Created {spec.name} ({spec.resource_id})")
    
    print(f"\nCreated {len(resources)} example resources in {args.base_path}")
    
    # Also create sample environment
    environment = create_sample_environment_with_resources()
    env_path = os.path.join("environments", "artisan-bakery-detailed.json")
    os.makedirs("environments", exist_ok=True)
    
    with open(env_path, 'w') as f:
        json.dump(environment, f, indent=2)
    
    print(f"Created sample environment: {env_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Resource Specification Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new resource
  python -m rhylthyme.resource_cli create --name "Commercial Mixer" \\
    --category mixer --manufacturer Hobart --model A-200 \\
    --capacity volume=20 --capacity unit=quarts \\
    --description "Heavy-duty stand mixer"
  
  # Add a photo to a resource
  python -m rhylthyme.resource_cli add-photo mixer_abc123 \\
    /path/to/mixer_photo.jpg --description "Front view of mixer"
  
  # List all resources
  python -m rhylthyme.resource_cli list
  
  # Search for resources
  python -m rhylthyme.resource_cli search "Hobart"
  
  # Create example bakery resources
  python -m rhylthyme.resource_cli create-examples
        """
    )
    
    parser.add_argument('--base-path', default='resources',
                       help='Base directory for resource data (default: resources)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create resource command
    create_parser = subparsers.add_parser('create', help='Create a new resource specification')
    create_parser.add_argument('--name', required=True, help='Resource name')
    create_parser.add_argument('--category', required=True, help='Resource category')
    create_parser.add_argument('--manufacturer', required=True, help='Manufacturer name')
    create_parser.add_argument('--model', required=True, help='Model number/name')
    create_parser.add_argument('--capacity', action='append',
                              help='Capacity specification (key=value format, can be used multiple times)')
    create_parser.add_argument('--description', help='Resource description')
    create_parser.add_argument('--serial-number', help='Serial number')
    create_parser.add_argument('--year-manufactured', type=int, help='Year manufactured')
    
    # Add photo command
    photo_parser = subparsers.add_parser('add-photo', help='Add a photo to a resource')
    photo_parser.add_argument('resource_id', help='Resource ID')
    photo_parser.add_argument('photo_path', help='Path to photo file')
    photo_parser.add_argument('--description', help='Photo description')
    photo_parser.add_argument('--photo-type', default='general',
                             choices=['general', 'manual', 'installation', 'maintenance', 'damage'],
                             help='Type of photo')
    
    # Add document command
    doc_parser = subparsers.add_parser('add-document', help='Add a document to a resource')
    doc_parser.add_argument('resource_id', help='Resource ID')
    doc_parser.add_argument('doc_path', help='Path to document file')
    doc_parser.add_argument('--description', help='Document description')
    doc_parser.add_argument('--doc-type', default='manual',
                           choices=['manual', 'spec_sheet', 'warranty', 'maintenance_log', 'certification'],
                           help='Type of document')
    
    # List resources command
    list_parser = subparsers.add_parser('list', help='List resource specifications')
    list_parser.add_argument('--category', help='Filter by category')
    
    # Show resource command
    show_parser = subparsers.add_parser('show', help='Show detailed resource information')
    show_parser.add_argument('resource_id', help='Resource ID to show')
    
    # Search resources command
    search_parser = subparsers.add_parser('search', help='Search resources')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--fields', help='Comma-separated list of fields to search in')
    
    # Export catalog command
    export_parser = subparsers.add_parser('export', help='Export resource catalog')
    export_parser.add_argument('output_file', help='Output file path')
    
    # Create examples command
    examples_parser = subparsers.add_parser('create-examples', 
                                           help='Create example bakery resources')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the appropriate command
    if args.command == 'create':
        create_resource_command(args)
    elif args.command == 'add-photo':
        add_photo_command(args)
    elif args.command == 'add-document':
        add_document_command(args)
    elif args.command == 'list':
        list_resources_command(args)
    elif args.command == 'show':
        show_resource_command(args)
    elif args.command == 'search':
        search_resources_command(args)
    elif args.command == 'export':
        export_catalog_command(args)
    elif args.command == 'create-examples':
        create_examples_command(args)


if __name__ == "__main__":
    main() 