#!/usr/bin/env python3
"""
Demo script showing the catalog selection functionality
for the NO3D Tools Asset Utility.

This script demonstrates how the catalog filtering works
and shows the different export options available.
"""

import json
from datetime import datetime

def create_mock_catalogs():
    """Create mock catalog data to demonstrate the functionality"""
    return {
        "Furniture": [
            {"name": "Modern Chair", "type": "MESH", "description": "Contemporary office chair"},
            {"name": "Wooden Table", "type": "MESH", "description": "Oak dining table"},
            {"name": "Leather Sofa", "type": "MESH", "description": "Three-seat leather sofa"}
        ],
        "Lighting": [
            {"name": "LED Strip", "type": "MESH", "description": "Flexible LED lighting strip"},
            {"name": "Pendant Light", "type": "MESH", "description": "Modern pendant light fixture"},
            {"name": "Floor Lamp", "type": "MESH", "description": "Adjustable floor lamp"}
        ],
        "Materials": [
            {"name": "Wood Texture", "type": "MATERIAL", "description": "Realistic wood grain material"},
            {"name": "Metal Shader", "type": "MATERIAL", "description": "Anisotropic metal material"},
            {"name": "Fabric Material", "type": "MATERIAL", "description": "Soft fabric material"}
        ]
    }

def generate_catalog_json(asset, catalog_name):
    """Generate JSON for an asset with catalog information"""
    return {
        "title": asset["name"],
        "handle": asset["name"].lower().replace(" ", "-"),
        "description": asset["description"],
        "vendor": "The Well Tarot",
        "product_type": "Blender Asset",
        "tags": ["blender", "3d", "asset", catalog_name.lower()],
        "status": "active",
        "variants": [{
            "price": "0.00",
            "sku": f"NO3D-{asset['name'].upper().replace(' ', '-')}",
            "inventory_policy": "continue",
            "inventory_management": "shopify"
        }],
        "metafields": [
            {
                "namespace": "no3d_tools",
                "key": "asset_type",
                "value": asset["type"],
                "type": "single_line_text_field"
            },
            {
                "namespace": "no3d_tools",
                "key": "catalog_name",
                "value": catalog_name,
                "type": "single_line_text_field"
            },
            {
                "namespace": "no3d_tools",
                "key": "export_date",
                "value": datetime.now().strftime("%Y-%m-%d"),
                "type": "date"
            }
        ]
    }

def demo_catalog_selection():
    """Demonstrate catalog selection functionality"""
    print("NO3D Tools Asset Utility - Catalog Selection Demo")
    print("=" * 60)
    
    # Create mock catalog data
    catalogs = create_mock_catalogs()
    
    print(f"Available Catalogs: {list(catalogs.keys())}")
    print()
    
    # Demo 1: Export all catalogs
    print("DEMO 1: Export All Catalogs")
    print("-" * 30)
    all_assets = []
    for catalog_name, assets in catalogs.items():
        all_assets.extend(assets)
        print(f"  {catalog_name}: {len(assets)} assets")
    
    print(f"Total assets across all catalogs: {len(all_assets)}")
    print()
    
    # Demo 2: Export specific catalog
    print("DEMO 2: Export Specific Catalog (Furniture)")
    print("-" * 40)
    furniture_assets = catalogs["Furniture"]
    print(f"Furniture catalog: {len(furniture_assets)} assets")
    for asset in furniture_assets:
        print(f"  - {asset['name']} ({asset['type']})")
    print()
    
    # Demo 3: Generate JSON for each catalog
    print("DEMO 3: Generated JSON with Catalog Information")
    print("-" * 45)
    
    for catalog_name, assets in catalogs.items():
        print(f"\n{catalog_name} Catalog JSON:")
        print("-" * 20)
        
        # Show JSON for first asset in each catalog
        if assets:
            sample_asset = assets[0]
            json_data = generate_catalog_json(sample_asset, catalog_name)
            
            # Show key information
            print(f"Title: {json_data['title']}")
            print(f"Handle: {json_data['handle']}")
            print(f"Catalog: {json_data['metafields'][1]['value']}")
            print(f"Asset Type: {json_data['metafields'][0]['value']}")
            print(f"Tags: {', '.join(json_data['tags'])}")
    
    print("\n" + "=" * 60)
    print("Catalog Selection Features:")
    print("✓ Filter assets by specific catalog")
    print("✓ Export all catalogs (excluding unassigned)")
    print("✓ Include catalog name in JSON metafields")
    print("✓ Support for different asset types per catalog")
    print("✓ Dynamic catalog detection")

def demo_export_scenarios():
    """Demonstrate different export scenarios"""
    print("\nEXPORT SCENARIOS:")
    print("=" * 20)
    
    scenarios = [
        {
            "name": "Export All Catalogs",
            "catalog": "All Catalogs",
            "description": "Exports assets from all catalogs, excluding unassigned assets",
            "use_case": "Complete asset library export"
        },
        {
            "name": "Export Furniture Only",
            "catalog": "Furniture",
            "description": "Exports only assets from the Furniture catalog",
            "use_case": "Category-specific export for furniture collection"
        },
        {
            "name": "Export Materials Only",
            "catalog": "Materials",
            "description": "Exports only material assets from Materials catalog",
            "use_case": "Material library export for texturing workflow"
        },
        {
            "name": "Export Local File Assets",
            "catalog": "Local File Catalogs",
            "description": "Exports assets from the current .blend file",
            "use_case": "Export assets from current project only"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Catalog: {scenario['catalog']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Use Case: {scenario['use_case']}")

if __name__ == "__main__":
    demo_catalog_selection()
    demo_export_scenarios()
    
    print("\n" + "=" * 60)
    print("To use this functionality in Blender:")
    print("1. Install the updated NO3D Tools Asset Utility")
    print("2. Open Asset Browser in Blender")
    print("3. Use the NO3D Export Tools panel")
    print("4. Select your desired catalog from the dropdown")
    print("5. Choose export options and click Export")
    print("=" * 60)
