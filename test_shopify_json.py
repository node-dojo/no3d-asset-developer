#!/usr/bin/env python3
"""
Test script to demonstrate the new Shopify-compatible JSON output format
for the NO3D Tools Asset Utility.

This script creates a mock asset and generates the JSON output
that would be created by the modified generate_asset_json function.
"""

import json
from datetime import datetime
import os

def create_mock_asset_data():
    """Create mock asset data to simulate a Blender asset"""
    return {
        'name': 'Dojo Bolt Gen v05',
        'type': 'MESH',
        'asset_data': {
            'description': 'Advanced bolt generation tool with customizable parameters for creating realistic bolts and fasteners in Blender.',
            'author': 'NO3D Tools',
            'tags': ['bolt', 'generator', 'modeling', 'hardware'],
            'license': 'MIT',
            'copyright': '2024 The Well Tarot'
        },
        'data': {
            'vertices': 1250,
            'edges': 1875,
            'polygons': 625,
            'materials': 2
        },
        'custom_properties': {
            'bolt_diameter': 8.0,
            'thread_pitch': 1.25,
            'head_type': 'hex',
            'material_grade': 'A2-70'
        }
    }

def generate_shopify_json(asset_data, catalog_name="Test Catalog"):
    """Generate Shopify-compatible JSON from mock asset data"""
    asset_name = asset_data['name']
    
    # Generate Shopify-compatible handle from asset name
    handle = asset_name.lower().replace(' ', '-').replace('_', '-')
    # Remove special characters and ensure it's URL-friendly
    import re
    handle = re.sub(r'[^a-z0-9\-]', '', handle)
    
    # Extract metadata
    asset_meta = asset_data.get('asset_data', {})
    description_text = asset_meta.get('description', '')
    author = asset_meta.get('author', '')
    tags = asset_meta.get('tags', [])
    
    # Build Shopify-compatible JSON structure
    json_data = {
        "title": asset_name,
        "handle": handle,
        "description": description_text or f"Blender asset: {asset_name}",
        "vendor": "The Well Tarot",
        "product_type": "Blender Add-on",
        "tags": tags + ["blender", "addon", "3d", "asset"],
        "status": "active",
        "variants": [
            {
                "price": "0.00",
                "sku": f"NO3D-TOOLS-{asset_name.upper().replace(' ', '-').replace('_', '-')}",
                "inventory_policy": "continue",
                "inventory_management": "shopify"
            }
        ],
        "metafields": [
            {
                "namespace": "no3d_tools",
                "key": "asset_type",
                "value": asset_data.get('type', 'UNKNOWN'),
                "type": "single_line_text_field"
            },
            {
                "namespace": "no3d_tools",
                "key": "blender_version",
                "value": "4.0+",
                "type": "single_line_text_field"
            },
            {
                "namespace": "no3d_tools",
                "key": "export_date",
                "value": datetime.now().strftime("%Y-%m-%d"),
                "type": "date"
            },
            {
                "namespace": "no3d_tools",
                "key": "source_file",
                "value": "test_asset.blend",
                "type": "single_line_text_field"
            }
        ]
    }
    
    # Add author to metafields if available
    if author:
        json_data["metafields"].append({
            "namespace": "no3d_tools",
            "key": "author",
            "value": author,
            "type": "single_line_text_field"
        })
    
    # Add geometry stats for mesh objects as metafields
    if asset_data.get('type') == 'MESH' and 'data' in asset_data:
        mesh_data = asset_data['data']
        json_data["metafields"].extend([
            {
                "namespace": "no3d_tools",
                "key": "vertices",
                "value": str(mesh_data.get('vertices', 0)),
                "type": "number_integer"
            },
            {
                "namespace": "no3d_tools",
                "key": "faces",
                "value": str(mesh_data.get('polygons', 0)),
                "type": "number_integer"
            },
            {
                "namespace": "no3d_tools",
                "key": "materials",
                "value": str(mesh_data.get('materials', 0)),
                "type": "number_integer"
            }
        ])
    
    # Add custom properties as metafields
    custom_props = asset_data.get('custom_properties', {})
    for key, value in custom_props.items():
        # Skip material_grade custom property
        if key.lower() == 'material_grade':
            continue
            
        # Determine metafield type based on value
        metafield_type = "single_line_text_field"
        if isinstance(value, (int, float)):
            metafield_type = "number_decimal" if isinstance(value, float) else "number_integer"
        elif isinstance(value, bool):
            metafield_type = "boolean"
        
        json_data["metafields"].append({
            "namespace": "no3d_tools",
            "key": f"custom_{key.lower().replace(' ', '_')}",
            "value": str(value),
            "type": metafield_type
        })
    
    # Add catalog information as metafield
    json_data["metafields"].append({
        "namespace": "no3d_tools",
        "key": "catalog_name",
        "value": catalog_name,
        "type": "single_line_text_field"
    })
    
    # Add file references as metafields
    json_data["metafields"].extend([
        {
            "namespace": "no3d_tools",
            "key": "blend_file",
            "value": f"{asset_name}.blend",
            "type": "single_line_text_field"
        },
        {
            "namespace": "no3d_tools",
            "key": "thumbnail",
            "value": f"icon_{asset_name}.png",
            "type": "single_line_text_field"
        }
    ])
    
    return json_data

def main():
    """Main test function"""
    print("NO3D Tools Asset Utility - Shopify JSON Output Test")
    print("=" * 60)
    
    # Create mock asset data
    mock_asset = create_mock_asset_data()
    print(f"Mock Asset: {mock_asset['name']}")
    print(f"Type: {mock_asset['type']}")
    print(f"Description: {mock_asset['asset_data']['description'][:50]}...")
    print()
    
    # Generate Shopify-compatible JSON
    shopify_json = generate_shopify_json(mock_asset, "Test Catalog")
    
    # Display the JSON output
    print("Generated Shopify-Compatible JSON:")
    print("-" * 40)
    print(json.dumps(shopify_json, indent=2))
    print()
    
    # Save to file for inspection
    output_file = "test_shopify_output.json"
    with open(output_file, 'w') as f:
        json.dump(shopify_json, f, indent=2)
    
    print(f"JSON output saved to: {output_file}")
    print()
    
    # Display key information
    print("Key Information:")
    print(f"  Title: {shopify_json['title']}")
    print(f"  Handle: {shopify_json['handle']}")
    print(f"  SKU: {shopify_json['variants'][0]['sku']}")
    print(f"  Metafields: {len(shopify_json['metafields'])} fields")
    print(f"  Tags: {', '.join(shopify_json['tags'])}")
    
    print("\nMetafields Summary:")
    for metafield in shopify_json['metafields']:
        print(f"  {metafield['namespace']}.{metafield['key']}: {metafield['value']} ({metafield['type']})")

if __name__ == "__main__":
    main()
