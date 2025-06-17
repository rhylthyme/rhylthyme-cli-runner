#!/usr/bin/env python3
"""
Resource Specification System

This module provides utilities for creating and managing detailed resource specifications
including equipment capacity, make/model information, and photo attachments.
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
import hashlib


@dataclass
class ResourceSpecification:
    """Detailed specification for a resource/equipment."""
    
    # Basic identification
    resource_id: str
    name: str
    category: str  # e.g., "oven", "mixer", "fryer", "prep-station"
    
    # Equipment details
    manufacturer: str
    model: str
    
    # Capacity specifications
    capacity: Dict[str, Union[float, str]]  # e.g., {"volume": 20, "unit": "quarts"}
    
    # Optional fields with defaults
    serial_number: Optional[str] = None
    year_manufactured: Optional[int] = None
    max_concurrent_users: int = 1
    
    # Physical specifications
    dimensions: Optional[Dict[str, float]] = None  # {"width": 24, "height": 18, "depth": 20, "unit": "inches"}
    weight: Optional[Dict[str, Union[float, str]]] = None  # {"value": 150, "unit": "lbs"}
    power_requirements: Optional[Dict[str, Any]] = None  # {"voltage": 220, "amperage": 30, "phase": 3}
    
    # Usage constraints
    qualified_actor_types: List[str] = None
    safety_requirements: List[str] = None
    maintenance_schedule: Optional[Dict[str, str]] = None
    
    # Documentation
    description: str = ""
    photos: List[Dict[str, str]] = None  # List of photo metadata
    manuals: List[Dict[str, str]] = None  # List of manual/documentation links
    certifications: List[str] = None
    
    # Operational data
    purchase_date: Optional[str] = None
    purchase_price: Optional[float] = None
    warranty_expiry: Optional[str] = None
    last_maintenance: Optional[str] = None
    condition: str = "good"  # "excellent", "good", "fair", "poor", "out-of-service"
    
    # Custom metadata
    custom_fields: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.qualified_actor_types is None:
            self.qualified_actor_types = []
        if self.safety_requirements is None:
            self.safety_requirements = []
        if self.photos is None:
            self.photos = []
        if self.manuals is None:
            self.manuals = []
        if self.certifications is None:
            self.certifications = []
        if self.custom_fields is None:
            self.custom_fields = {}


class ResourceSpecManager:
    """Manager for resource specifications with photo and documentation support."""
    
    def __init__(self, base_path: str = "resources"):
        """
        Initialize the resource specification manager.
        
        Args:
            base_path: Base directory for storing resource data
        """
        self.base_path = base_path
        self.specs_dir = os.path.join(base_path, "specs")
        self.photos_dir = os.path.join(base_path, "photos")
        self.docs_dir = os.path.join(base_path, "docs")
        
        # Create directories if they don't exist
        os.makedirs(self.specs_dir, exist_ok=True)
        os.makedirs(self.photos_dir, exist_ok=True)
        os.makedirs(self.docs_dir, exist_ok=True)
    
    def create_resource_spec(self, 
                           name: str,
                           category: str,
                           manufacturer: str,
                           model: str,
                           capacity: Dict[str, Union[float, str]],
                           **kwargs) -> ResourceSpecification:
        """
        Create a new resource specification.
        
        Args:
            name: Resource name
            category: Resource category
            manufacturer: Equipment manufacturer
            model: Model number/name
            capacity: Capacity specifications
            **kwargs: Additional specification fields
            
        Returns:
            ResourceSpecification object
        """
        resource_id = kwargs.get('resource_id', f"{category}_{uuid.uuid4().hex[:8]}")
        
        spec = ResourceSpecification(
            resource_id=resource_id,
            name=name,
            category=category,
            manufacturer=manufacturer,
            model=model,
            capacity=capacity,
            **kwargs
        )
        
        return spec
    
    def save_resource_spec(self, spec: ResourceSpecification) -> str:
        """
        Save a resource specification to disk.
        
        Args:
            spec: ResourceSpecification to save
            
        Returns:
            Path to saved file
        """
        file_path = os.path.join(self.specs_dir, f"{spec.resource_id}.json")
        
        # Convert to dict and handle datetime serialization
        spec_dict = asdict(spec)
        
        with open(file_path, 'w') as f:
            json.dump(spec_dict, f, indent=2, default=str)
        
        return file_path
    
    def load_resource_spec(self, resource_id: str) -> Optional[ResourceSpecification]:
        """
        Load a resource specification from disk.
        
        Args:
            resource_id: ID of the resource to load
            
        Returns:
            ResourceSpecification object or None if not found
        """
        file_path = os.path.join(self.specs_dir, f"{resource_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            spec_dict = json.load(f)
        
        return ResourceSpecification(**spec_dict)
    
    def add_photo(self, 
                  resource_id: str, 
                  photo_path: str, 
                  description: str = "",
                  photo_type: str = "general") -> str:
        """
        Add a photo to a resource specification.
        
        Args:
            resource_id: ID of the resource
            photo_path: Path to the photo file
            description: Photo description
            photo_type: Type of photo (general, manual, installation, etc.)
            
        Returns:
            Photo ID
        """
        spec = self.load_resource_spec(resource_id)
        if not spec:
            raise ValueError(f"Resource {resource_id} not found")
        
        # Generate unique photo ID
        photo_id = f"photo_{uuid.uuid4().hex[:8]}"
        
        # Copy photo to photos directory
        photo_filename = f"{resource_id}_{photo_id}{os.path.splitext(photo_path)[1]}"
        photo_dest = os.path.join(self.photos_dir, photo_filename)
        
        # Calculate file hash for integrity checking
        with open(photo_path, 'rb') as f:
            photo_hash = hashlib.md5(f.read()).hexdigest()
        
        # Copy file
        import shutil
        shutil.copy2(photo_path, photo_dest)
        
        # Add photo metadata to spec
        photo_metadata = {
            "photo_id": photo_id,
            "filename": photo_filename,
            "original_path": photo_path,
            "description": description,
            "photo_type": photo_type,
            "upload_date": datetime.now().isoformat(),
            "file_hash": photo_hash,
            "file_size": os.path.getsize(photo_dest)
        }
        
        spec.photos.append(photo_metadata)
        self.save_resource_spec(spec)
        
        return photo_id
    
    def add_document(self,
                    resource_id: str,
                    doc_path: str,
                    doc_type: str = "manual",
                    description: str = "") -> str:
        """
        Add a document (manual, spec sheet, etc.) to a resource.
        
        Args:
            resource_id: ID of the resource
            doc_path: Path to the document file
            doc_type: Type of document (manual, spec_sheet, warranty, etc.)
            description: Document description
            
        Returns:
            Document ID
        """
        spec = self.load_resource_spec(resource_id)
        if not spec:
            raise ValueError(f"Resource {resource_id} not found")
        
        # Generate unique document ID
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        # Copy document to docs directory
        doc_filename = f"{resource_id}_{doc_id}{os.path.splitext(doc_path)[1]}"
        doc_dest = os.path.join(self.docs_dir, doc_filename)
        
        # Calculate file hash
        with open(doc_path, 'rb') as f:
            doc_hash = hashlib.md5(f.read()).hexdigest()
        
        # Copy file
        import shutil
        shutil.copy2(doc_path, doc_dest)
        
        # Add document metadata to spec
        doc_metadata = {
            "doc_id": doc_id,
            "filename": doc_filename,
            "original_path": doc_path,
            "doc_type": doc_type,
            "description": description,
            "upload_date": datetime.now().isoformat(),
            "file_hash": doc_hash,
            "file_size": os.path.getsize(doc_dest)
        }
        
        spec.manuals.append(doc_metadata)
        self.save_resource_spec(spec)
        
        return doc_id
    
    def list_resources(self, category: Optional[str] = None) -> List[ResourceSpecification]:
        """
        List all resource specifications, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of ResourceSpecification objects
        """
        resources = []
        
        for filename in os.listdir(self.specs_dir):
            if filename.endswith('.json'):
                resource_id = filename[:-5]  # Remove .json extension
                spec = self.load_resource_spec(resource_id)
                if spec and (category is None or spec.category == category):
                    resources.append(spec)
        
        return resources
    
    def get_photo_path(self, resource_id: str, photo_id: str) -> Optional[str]:
        """
        Get the file path for a specific photo.
        
        Args:
            resource_id: ID of the resource
            photo_id: ID of the photo
            
        Returns:
            Photo file path or None if not found
        """
        spec = self.load_resource_spec(resource_id)
        if not spec:
            return None
        
        for photo in spec.photos:
            if photo["photo_id"] == photo_id:
                return os.path.join(self.photos_dir, photo["filename"])
        
        return None
    
    def export_resource_catalog(self, output_path: str) -> None:
        """
        Export a complete resource catalog to JSON.
        
        Args:
            output_path: Path for the output catalog file
        """
        catalog = {
            "catalog_id": f"catalog_{uuid.uuid4().hex[:8]}",
            "created_date": datetime.now().isoformat(),
            "resources": []
        }
        
        for spec in self.list_resources():
            catalog["resources"].append(asdict(spec))
        
        with open(output_path, 'w') as f:
            json.dump(catalog, f, indent=2, default=str)
    
    def search_resources(self, 
                        query: str, 
                        fields: List[str] = None) -> List[ResourceSpecification]:
        """
        Search resources by text query across specified fields.
        
        Args:
            query: Search query
            fields: Fields to search in (default: name, manufacturer, model, description)
            
        Returns:
            List of matching ResourceSpecification objects
        """
        if fields is None:
            fields = ["name", "manufacturer", "model", "description"]
        
        query_lower = query.lower()
        results = []
        
        for spec in self.list_resources():
            for field in fields:
                field_value = getattr(spec, field, "")
                if field_value and query_lower in str(field_value).lower():
                    results.append(spec)
                    break
        
        return results


def create_bakery_resources() -> Dict[str, ResourceSpecification]:
    """Create example resource specifications for a bakery."""
    
    manager = ResourceSpecManager()
    
    # Commercial Mixer
    mixer_spec = manager.create_resource_spec(
        name="20-Quart Commercial Stand Mixer",
        category="mixer",
        manufacturer="Hobart",
        model="A-200",
        capacity={"volume": 20, "unit": "quarts", "max_batch_size": "12 lbs dough"},
        serial_number="H200-2023-001",
        year_manufactured=2023,
        max_concurrent_users=1,
        dimensions={"width": 23.5, "height": 31.5, "depth": 17.5, "unit": "inches"},
        weight={"value": 165, "unit": "lbs"},
        power_requirements={
            "voltage": 115,
            "amperage": 15,
            "phase": 1,
            "horsepower": 1/3
        },
        qualified_actor_types=["head-baker", "pastry-chef", "baker", "assistant-baker"],
        safety_requirements=[
            "safety_guard_required",
            "training_certification",
            "no_loose_clothing",
            "tie_back_long_hair"
        ],
        maintenance_schedule={
            "daily": "clean_bowl_and_attachments",
            "weekly": "lubricate_planetary_gear",
            "monthly": "inspect_drive_belt",
            "quarterly": "professional_service"
        },
        description="Heavy-duty commercial stand mixer for bread, cake, and pastry production",
        certifications=["NSF", "UL", "ETL"],
        purchase_date="2023-06-15",
        purchase_price=2850.00,
        warranty_expiry="2025-06-15",
        condition="excellent",
        custom_fields={
            "attachments": ["dough_hook", "wire_whip", "flat_beater"],
            "optional_attachments": ["pastry_knife", "wing_whip"],
            "noise_level": "68 dB",
            "duty_cycle": "continuous"
        }
    )
    
    # Commercial Convection Oven
    oven_spec = manager.create_resource_spec(
        name="Double Deck Convection Oven",
        category="oven",
        manufacturer="Blodgett",
        model="DFG-200-ES",
        capacity={
            "chambers": 2,
            "pan_capacity_per_chamber": 5,
            "pan_size": "18x26 inch",
            "temperature_range": "200-500°F"
        },
        serial_number="BDG-2023-445",
        year_manufactured=2023,
        max_concurrent_users=2,
        dimensions={"width": 38, "height": 61, "depth": 32, "unit": "inches"},
        weight={"value": 685, "unit": "lbs"},
        power_requirements={
            "fuel_type": "natural_gas",
            "gas_input": "120,000 BTU/hr per chamber",
            "electrical": "115V, 60Hz, 1-phase for controls"
        },
        qualified_actor_types=["head-baker", "pastry-chef", "baker"],
        safety_requirements=[
            "heat_resistant_gloves",
            "safety_training",
            "proper_ventilation",
            "fire_suppression_access"
        ],
        maintenance_schedule={
            "daily": "clean_interior_and_racks",
            "weekly": "check_door_seals",
            "monthly": "calibrate_temperature",
            "annually": "professional_gas_inspection"
        },
        description="Energy-efficient double deck convection oven for high-volume baking",
        certifications=["NSF", "CSA", "ENERGY_STAR"],
        purchase_date="2023-05-20",
        purchase_price=8900.00,
        warranty_expiry="2026-05-20",
        condition="excellent",
        custom_fields={
            "steam_injection": True,
            "digital_controls": True,
            "programmable_recipes": 99,
            "energy_efficiency": "ENERGY STAR certified"
        }
    )
    
    # Proof Box
    proof_box_spec = manager.create_resource_spec(
        name="Mobile Proofing Cabinet",
        category="proofer",
        manufacturer="Carter-Hoffmann",
        model="PH1845",
        capacity={
            "pan_capacity": 18,
            "pan_size": "18x26 inch",
            "humidity_range": "15-85%",
            "temperature_range": "70-185°F"
        },
        serial_number="CH-2023-789",
        year_manufactured=2023,
        max_concurrent_users=1,
        dimensions={"width": 30.5, "height": 73, "depth": 28.5, "unit": "inches"},
        weight={"value": 295, "unit": "lbs"},
        power_requirements={
            "voltage": 208,
            "amperage": 16.7,
            "phase": 3,
            "wattage": 6000
        },
        qualified_actor_types=["head-baker", "pastry-chef", "baker", "assistant-baker"],
        safety_requirements=[
            "steam_safety_training",
            "heat_resistant_gloves",
            "proper_ventilation"
        ],
        maintenance_schedule={
            "daily": "drain_water_reservoir",
            "weekly": "clean_humidity_generator",
            "monthly": "descale_water_system",
            "quarterly": "inspect_door_gaskets"
        },
        description="Mobile proofing cabinet with precise humidity and temperature control",
        certifications=["NSF", "UL"],
        purchase_date="2023-07-10",
        purchase_price=4200.00,
        warranty_expiry="2025-07-10",
        condition="excellent",
        custom_fields={
            "mobile": True,
            "digital_controls": True,
            "automatic_water_fill": True,
            "insulation_type": "polyurethane_foam"
        }
    )
    
    return {
        "commercial_mixer": mixer_spec,
        "convection_oven": oven_spec,
        "proof_box": proof_box_spec
    }


def create_sample_environment_with_resources() -> Dict[str, Any]:
    """Create a sample environment that references detailed resource specifications."""
    
    # Create the resource specs
    resources = create_bakery_resources()
    
    # Create environment that references these resources
    environment = {
        "environmentId": "artisan-bakery-detailed",
        "name": "Artisan Bakery with Detailed Equipment Specs",
        "description": "Professional bakery environment with comprehensive equipment specifications",
        "type": "bakery",
        
        # Detailed resource specifications
        "resourceSpecifications": {
            spec.resource_id: asdict(spec) for spec in resources.values()
        },
        
        # Actor types
        "actorTypes": {
            "head-baker": {
                "name": "Head Baker",
                "count": 1,
                "description": "Master baker, can operate all equipment",
                "qualifications": ["commercial_baking_certification", "food_safety", "equipment_training"]
            },
            "pastry-chef": {
                "name": "Pastry Chef",
                "count": 1,
                "description": "Specialized in pastries, desserts, and decorative work",
                "qualifications": ["pastry_certification", "decorating_skills", "equipment_training"]
            },
            "baker": {
                "name": "Baker",
                "count": 2,
                "description": "Experienced baker for bread and general production",
                "qualifications": ["baking_experience", "food_safety", "basic_equipment_training"]
            },
            "assistant-baker": {
                "name": "Assistant Baker",
                "count": 2,
                "description": "Entry-level position, assists with production",
                "qualifications": ["food_safety", "basic_training"]
            }
        },
        
        # Resource constraints that reference detailed specs
        "resourceConstraints": [
            {
                "task": "mixing",
                "maxConcurrent": 1,
                "actorsRequired": 1.0,
                "qualifiedActorTypes": ["head-baker", "pastry-chef", "baker", "assistant-baker"],
                "description": "20-quart commercial mixer operations",
                "resourceSpecId": "mixer_a200_001",  # Reference to detailed spec
                "capacityMetrics": {
                    "max_batch_volume": 20,
                    "unit": "quarts",
                    "throughput_per_hour": 8
                }
            },
            {
                "task": "baking",
                "maxConcurrent": 2,
                "actorsRequired": 0.5,
                "qualifiedActorTypes": ["head-baker", "pastry-chef", "baker"],
                "description": "Double deck convection oven operations",
                "resourceSpecId": "oven_dfg200_001",
                "capacityMetrics": {
                    "chambers": 2,
                    "pans_per_chamber": 5,
                    "bake_cycles_per_hour": 4
                }
            },
            {
                "task": "proofing",
                "maxConcurrent": 1,
                "actorsRequired": 0.2,
                "qualifiedActorTypes": ["head-baker", "pastry-chef", "baker", "assistant-baker"],
                "description": "Proofing cabinet operations",
                "resourceSpecId": "proofer_ph1845_001",
                "capacityMetrics": {
                    "pan_capacity": 18,
                    "proof_cycles_per_day": 6
                }
            }
        ],
        
        # Operating metadata
        "metadata": {
            "capacity": "medium",
            "specialties": ["artisan_bread", "pastries", "custom_cakes"],
            "operating_hours": "4am-6pm",
            "daily_production": "800 units",
            "equipment_value": 16050.00,
            "last_equipment_audit": "2023-08-01"
        }
    }
    
    return environment 