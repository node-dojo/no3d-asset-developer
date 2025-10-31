import bpy
import json
import os
from datetime import datetime
from bpy.types import Context


def get_selected_assets(context: Context):
    """Query Asset Browser for selected assets and return list of asset data blocks."""
    selected_assets = []
    
    # Try to get selected asset from context
    if hasattr(context, 'id') and context.id:
        asset = context.id
        if hasattr(asset, 'asset_data') and asset.asset_data:
            selected_assets.append(asset)
            return selected_assets
    
    # Fallback: Get all assets from current file
    # This will be used when called from context menu
    all_assets = get_all_visible_assets(context)
    
    # For now, return all assets if specific selection can't be determined
    # In a real implementation, you'd check the Asset Browser's selection state
    return all_assets


def get_available_catalogs():
    """Get list of available asset catalogs in the current file."""
    catalogs = []
    
    # Get all asset catalogs from the current file
    for catalog in bpy.data.asset_libraries:
        if hasattr(catalog, 'name') and catalog.name:
            catalogs.append(catalog.name)
    
    # Also check for local catalogs (catalogs defined in the current .blend file)
    # In Blender 4.0+, catalogs are stored in the file's asset library
    try:
        # Get the current file's asset library
        current_file_library = bpy.data.filepath
        if current_file_library:
            # For local catalogs, we'll use a special identifier
            catalogs.append("Local File Catalogs")
    except:
        pass
    
    # If no catalogs found, return a default option
    if not catalogs:
        catalogs = ["Default"]
    
    return catalogs


def get_assets_by_catalog(catalog_name, asset_type_filter='ALL'):
    """Get assets from a specific catalog."""
    all_assets = []
    
    # If "All Catalogs" is selected, get all assets
    if catalog_name == "All Catalogs":
        return get_all_visible_assets(None, asset_type_filter)
    
    # If "Local File Catalogs" is selected, get assets from the current file
    if catalog_name == "Local File Catalogs":
        return get_all_visible_assets(None, asset_type_filter)
    
    # For specific catalogs, we need to filter by catalog
    # Note: This is a simplified implementation as Blender's catalog API is complex
    all_assets = get_all_visible_assets(None, asset_type_filter)
    
    # Filter assets by catalog (this would need to be enhanced based on actual catalog data)
    filtered_assets = []
    for asset in all_assets:
        # Check if asset belongs to the specified catalog
        # This is a placeholder - actual implementation would check asset.catalog_id
        if hasattr(asset, 'asset_data') and asset.asset_data:
            # For now, we'll include all assets as catalog filtering is complex
            # In a real implementation, you'd check the asset's catalog assignment
            filtered_assets.append(asset)
    
    return filtered_assets


def get_all_visible_assets(context: Context, asset_type_filter='ALL'):
    """Query current Asset Library catalog and return all assets matching current filter."""
    all_assets = []
    
    # Get all objects with asset data
    if asset_type_filter in ('ALL', 'OBJECT'):
        for obj in bpy.data.objects:
            if hasattr(obj, 'asset_data') and obj.asset_data:
                all_assets.append(obj)
                print(f"DEBUG: Found object asset: {obj.name}")
    
    # Get all materials with asset data
    if asset_type_filter in ('ALL', 'MATERIAL'):
        for mat in bpy.data.materials:
            if hasattr(mat, 'asset_data') and mat.asset_data:
                all_assets.append(mat)
                print(f"DEBUG: Found material asset: {mat.name}")
    
    # Get all node groups with asset data
    if asset_type_filter in ('ALL', 'NODE_TREE'):
        for node_group in bpy.data.node_groups:
            if hasattr(node_group, 'asset_data') and node_group.asset_data:
                all_assets.append(node_group)
                print(f"DEBUG: Found node group asset: {node_group.name}")
    
    # Get all collections with asset data
    if asset_type_filter in ('ALL', 'COLLECTION'):
        for col in bpy.data.collections:
            if hasattr(col, 'asset_data') and col.asset_data:
                all_assets.append(col)
                print(f"DEBUG: Found collection asset: {col.name}")
    
    # Get all worlds with asset data
    if asset_type_filter == 'ALL':
        for world in bpy.data.worlds:
            if hasattr(world, 'asset_data') and world.asset_data:
                all_assets.append(world)
                print(f"DEBUG: Found world asset: {world.name}")
    
    # Get all brushes with asset data
    if asset_type_filter == 'ALL':
        for brush in bpy.data.brushes:
            if hasattr(brush, 'asset_data') and brush.asset_data:
                all_assets.append(brush)
                print(f"DEBUG: Found brush asset: {brush.name}")
    
    return all_assets


def export_asset_blend(asset, target_dir: str):
    """Export asset as individual .blend file with proper scene units using data blocks library."""
    asset_name = getattr(asset, 'name', 'asset')
    
    # Create individual folder for this asset
    asset_folder = os.path.join(target_dir, asset_name)
    os.makedirs(asset_folder, exist_ok=True)
    
    filepath = os.path.join(asset_folder, f"{asset_name}.blend")
    
    try:
        # Get asset type
        asset_type = type(asset).__name__
        
        # Create data blocks list for this asset
        data_blocks = set()
        data_blocks.add(asset)
        
        # For objects, also include mesh data
        if asset_type == 'Object' and asset.data:
            data_blocks.add(asset.data)
            # Include materials
            if hasattr(asset.data, 'materials'):
                for mat in asset.data.materials:
                    if mat:
                        data_blocks.add(mat)
        
        # For collections, include all objects and their data
        elif asset_type == 'Collection':
            for obj in asset.objects:
                data_blocks.add(obj)
                if obj.data:
                    data_blocks.add(obj.data)
                if hasattr(obj.data, 'materials'):
                    for mat in obj.data.materials:
                        if mat:
                            data_blocks.add(mat)
        
        # Use bpy.data.libraries.write to write just this asset to a file
        # This writes a minimal .blend file with only the specified data blocks
        bpy.data.libraries.write(
            filepath,
            data_blocks,
            path_remap='RELATIVE',
            fake_user=True,
            compress=True
        )
        
        print(f"Exported {asset_name} ({asset_type}) to {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error exporting asset {asset_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_file_size(filepath):
    """Get file size in bytes."""
    try:
        return os.path.getsize(filepath)
    except (OSError, FileNotFoundError):
        return 0


def generate_asset_markdown(asset, target_dir: str, catalog_name="Unknown"):
    """Generate markdown description file for the asset."""
    try:
        asset_name = getattr(asset, 'name', 'asset')
        
        # Create individual folder for this asset
        asset_folder = os.path.join(target_dir, asset_name)
        os.makedirs(asset_folder, exist_ok=True)
        
        # Extract metadata from asset.asset_data
        asset_data = getattr(asset, 'asset_data', None)
        
        # Generate handle from asset name
        handle = asset_name.lower().replace(' ', '-').replace('_', '-')
        import re
        handle = re.sub(r'[^a-z0-9\-]', '', handle)
        
        # Extract description and other metadata
        description_text = ""
        author = ""
        tags = []
        if asset_data:
            description_text = getattr(asset_data, 'description', '')
            author = getattr(asset_data, 'author', '')
            tags = [tag.name for tag in getattr(asset_data, 'tags', [])]
        
        # Get asset type
        asset_type = type(asset).__name__
        
        # Get Blender version
        blender_version = f"{bpy.app.version[0]}.{bpy.app.version[1]}.{bpy.app.version[2]}+"
        
        # Get file size
        blend_file_path = os.path.join(asset_folder, f"{asset_name}.blend")
        file_size = get_file_size(blend_file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2) if file_size > 0 else 0
        
        # Generate markdown content
        markdown_content = f"""---
title: "{asset_name}"
description: "{description_text or f'Blender asset: {asset_name}'}"
version: "1.0.0"
blender_version: "{blender_version}"
asset_type: "{asset_type}"
tags: {json.dumps(tags + ['blender', 'addon', '3d', 'asset'])}
author: "{author or 'The Well Tarot'}"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
file_size_mb: {file_size_mb}
catalog: "{catalog_name}"
handle: "{handle}"
sku: "NO3D-TOOLS-{asset_name.upper().replace(' ', '-').replace('_', '-')}"
---

# {asset_name}

## Description

{description_text or f'Detailed description of the {asset_name} Blender asset.'}

## Features

- **Asset Type**: {asset_type}
- **Blender Version**: {blender_version}
- **File Size**: {file_size_mb} MB
- **Catalog**: {catalog_name}

## Usage Instructions

### Basic Usage

1. Download the `.blend` file
2. Open in Blender {blender_version}
3. Import or drag the asset into your scene
4. Use the asset as needed

### Advanced Usage

- Customize the asset parameters
- Combine with other assets
- Use in your own projects

## Technical Details

- **Blender Version**: {blender_version}
- **Asset Type**: {asset_type}
- **File Size**: {file_size_mb} MB
- **Dependencies**: None

## Examples

This asset can be used for:
- 3D modeling projects
- Animation workflows
- Game development
- Architectural visualization

## Changelog

### Version 1.0.0
- Initial release
- Core functionality

## Support

For questions or issues with this asset, please contact The Well Tarot.

## License

Commercial use license included.
"""
        
        # Save markdown file
        markdown_path = os.path.join(asset_folder, f"{asset_name}_desc.md")
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Generated markdown description: {markdown_path}")
        return markdown_path
        
    except Exception as e:
        print(f"Error generating markdown for asset {asset_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_asset_json(asset, target_dir: str, catalog_name="Unknown"):
    """Generate Shopify-compatible JSON metadata file for the asset."""
    try:
        asset_name = getattr(asset, 'name', 'asset')
        
        # Create individual folder for this asset
        asset_folder = os.path.join(target_dir, asset_name)
        os.makedirs(asset_folder, exist_ok=True)
        
        # Extract metadata from asset.asset_data
        asset_data = getattr(asset, 'asset_data', None)
        
        # Generate Shopify-compatible handle from asset name
        handle = asset_name.lower().replace(' ', '-').replace('_', '-')
        # Remove special characters and ensure it's URL-friendly
        import re
        handle = re.sub(r'[^a-z0-9\-]', '', handle)
        
        # Extract description and other metadata
        description_text = ""
        author = ""
        tags = []
        if asset_data:
            description_text = getattr(asset_data, 'description', '')
            author = getattr(asset_data, 'author', '')
            tags = [tag.name for tag in getattr(asset_data, 'tags', [])]
        
        # Build dual-format JSON structure (Shopify + Polar compatible)
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
                    "inventory_management": "polar"
                }
            ],
            "metafields": [
                {
                    "namespace": "no3d_tools",
                    "key": "asset_type",
                    "value": getattr(asset, 'type', 'UNKNOWN'),
                    "type": "single_line_text_field"
                },
                {
                    "namespace": "no3d_tools",
                    "key": "blender_version",
                    "value": f"{bpy.app.version[0]}.{bpy.app.version[1]}.{bpy.app.version[2]}+",
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
                    "value": os.path.basename(bpy.data.filepath) if bpy.data.filepath else "unknown",
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
        if hasattr(asset, 'type') and asset.type == 'MESH' and hasattr(asset, 'data'):
            mesh = asset.data
            json_data["metafields"].extend([
                {
                    "namespace": "no3d_tools",
                    "key": "vertices",
                    "value": str(len(mesh.vertices)),
                    "type": "number_integer"
                },
                {
                    "namespace": "no3d_tools",
                    "key": "faces",
                    "value": str(len(mesh.polygons)),
                    "type": "number_integer"
                },
                {
                    "namespace": "no3d_tools",
                    "key": "materials",
                    "value": str(len(mesh.materials)),
                    "type": "number_integer"
            }
            ])
        
        # Add custom properties as metafields
        if hasattr(asset, 'items'):
            custom_props = dict(asset.items())
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
        
        # Add Polar-specific metafields
        json_data["metafields"].extend([
            {
                "namespace": "polar",
                "key": "file_download_url",
                "value": f"https://polar.sh/the-well-tarot/products/{handle}",
                "type": "single_line_text_field"
            },
            {
                "namespace": "polar",
                "key": "file_size_bytes",
                "value": str(get_file_size(os.path.join(asset_folder, f"{asset_name}.blend"))),
                "type": "number_integer"
            },
            {
                "namespace": "polar",
                "key": "file_type",
                "value": "blend",
                "type": "single_line_text_field"
            },
            {
                "namespace": "polar",
                "key": "download_count",
                "value": "0",
                "type": "number_integer"
            },
            {
                "namespace": "polar",
                "key": "license_type",
                "value": "commercial",
                "type": "single_line_text_field"
            },
            {
                "namespace": "polar",
                "key": "compatibility",
                "value": f"Blender {bpy.app.version[0]}.{bpy.app.version[1]}+",
                "type": "single_line_text_field"
            }
        ])
        
        # Save JSON file
        json_path = os.path.join(asset_folder, f"{asset_name}.json")
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save description as separate text file
        if description_text:
            desc_path = os.path.join(asset_folder, f"desc_{asset_name}.txt")
            with open(desc_path, 'w', encoding='utf-8') as f:
                f.write(description_text)
            print(f"Saved description to {desc_path}")
        
        return json_path
        
    except Exception as e:
        print(f"Error generating JSON for asset {asset_name}: {e}")
        import traceback
        traceback.print_exc()
        return None


def export_asset_thumbnail(asset, target_dir: str):
    """Export asset thumbnail as PNG image."""
    try:
        asset_name = getattr(asset, 'name', 'asset')
        
        # Create individual folder for this asset
        asset_folder = os.path.join(target_dir, asset_name)
        os.makedirs(asset_folder, exist_ok=True)
        
        # Get asset preview
        asset_data = getattr(asset, 'asset_data', None)
        if not asset_data:
            print(f"No asset data found for {asset_name}")
            return None
        
        # Try to render a simple preview using Blender's preview rendering
        thumbnail_path = os.path.join(asset_folder, f"icon_{asset_name}.png")
        
        # Get the asset's preview image from Blender's preview system
        preview = asset.preview
        if preview and preview.image_size[0] > 0:
            # Extract preview pixel data
            pixels = list(preview.image_pixels_float)
            
            if len(pixels) > 0:
                # Convert float pixels to bytes (RGBA format)
                import array
                width, height = preview.image_size
                
                # Create image data structure
                # Blender stores previews as float RGBA, need to convert to byte RGBA
                pixel_bytes = array.array('B')
                for i in range(0, len(pixels), 4):
                    # Convert float (0.0-1.0) to byte (0-255)
                    r = int(pixels[i] * 255)
                    g = int(pixels[i+1] * 255)
                    b = int(pixels[i+2] * 255)
                    a = int(pixels[i+3] * 255)
                    pixel_bytes.extend([r, g, b, a])
                
                # Create a temporary image in Blender
                temp_image = bpy.data.images.new(
                    name=f"temp_preview_{asset_name}",
                    width=width,
                    height=height,
                    alpha=True
                )
                
                # Set the pixels
                temp_image.pixels = [p/255.0 for p in pixel_bytes]
                
                # Save the image
                temp_image.filepath_raw = thumbnail_path
                temp_image.file_format = 'PNG'
                temp_image.save()
                
                # Clean up
                bpy.data.images.remove(temp_image)
                
                print(f"Exported thumbnail for {asset_name} to {thumbnail_path}")
                return thumbnail_path
            else:
                print(f"Preview exists but has no pixel data for {asset_name}")
                return None
        else:
            print(f"No preview image available for {asset_name}")
            return None
        
    except Exception as e:
        print(f"Error exporting thumbnail for asset {asset_name}: {e}")
        import traceback
        traceback.print_exc()
        return None
