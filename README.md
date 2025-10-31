# NO3D Tools Asset Utility

A Blender 4.5+ add-on that extends the Asset Browser with export functionality for individual assets with metadata and thumbnails.

## Features

- **Export All Assets**: Export all assets with .blend files, JSON metadata, thumbnails, and descriptions (includes filter options)
- **Export Thumbnails Only**: Quickly export only thumbnail/icon images for all assets
- **Organized Folders**: Each asset is exported into its own named folder with all related files
- **Individual .blend Files**: Each asset is exported as a separate .blend file with proper scene units
- **JSON Metadata**: Automatic generation of JSON files with complete asset metadata
- **PNG Thumbnails**: Export asset preview images as `icon_{asset_name}.png`
- **Description Files**: Export asset descriptions as `desc_{asset_name}.txt`
- **Proper Scene Units**: Exported .blend files maintain metric system with 0.001 scale and millimeter units

## Installation

1. Download the `NO3D_Tools_Asset_Utility` zip file
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install..." and select the zip file
4. Enable the add-on by checking the box next to "NO3D Tools Asset Utility"

### Updating from Previous Version

If you're updating from an older version:
1. **Disable the old add-on** (uncheck it in Preferences)
2. **Restart Blender** (important for clearing cached modules)
3. **Remove the old version** (click "Remove" button)
4. Install the new version as described above

## Usage

### IMPORTANT: Asset Library Limitation

**This add-on currently exports assets from the CURRENT .blend file, not from external Asset Libraries.**

When you use the Asset Browser to browse external libraries, those assets are not loaded into the current file. To export them:

1. **Open the .blend file** that contains your assets (the actual source file)
2. Make sure objects/materials/collections in that file are marked as assets
3. Use the export operators from the context menu or N-panel

### Export Workflow

**Option 1: From Current File (Recommended)**
1. Open the .blend file containing your assets
2. Right-click in the Asset Browser (or use N-panel > NO3D tab if available)
3. Choose "NO3D Export Tools" > "Export All Visible Assets..."
4. Select your target directory
5. The add-on will export all assets marked in the current file

**Option 2: Context Menu**
1. Right-click in the Asset Browser
2. Choose "NO3D Export Tools"
3. Select your export option:
   - **Export All Assets** - Complete export with .blend, JSON, thumbnails, and descriptions (with filter options)
   - **Export Thumbnails Only** - Fast export of only icon images
4. Choose your export directory and configure options (asset type filter, etc.)

## Export Options

- **Export JSON Metadata**: Generates a JSON file for each asset containing:
  - Asset name, type, and description
  - Author, copyright, and license information
  - Tags and catalog information
  - Export date and Blender version
  - Geometry statistics (for mesh objects)
  - Custom properties

- **Export Thumbnails**: Saves asset preview images as PNG files (`icon_{asset_name}.png`)
- **Export Descriptions**: Saves asset description text as separate TXT files (`desc_{asset_name}.txt`)

## File Structure

The add-on creates individual folders for each exported asset with all related files organized inside:

```
target_directory/
├── Asset_Name_1/
│   ├── Asset_Name_1.blend          # Individual .blend file with proper scene units
│   ├── Asset_Name_1.json           # Complete metadata file
│   ├── icon_Asset_Name_1.png       # Asset thumbnail/preview image
│   └── desc_Asset_Name_1.txt       # Asset description text
├── Asset_Name_2/
│   ├── Asset_Name_2.blend
│   ├── Asset_Name_2.json
│   ├── icon_Asset_Name_2.png
│   └── desc_Asset_Name_2.txt
└── Asset_Name_3/
    ├── Asset_Name_3.blend
    ├── Asset_Name_3.json
    ├── icon_Asset_Name_3.png
    └── desc_Asset_Name_3.txt
```

Each asset gets its own folder named after the asset, keeping all related files organized together.

## JSON Metadata Structure

The add-on now generates **Shopify-compatible JSON** output for easy integration with e-commerce platforms:

```json
{
  "title": "Dojo Bolt Gen v05",
  "handle": "dojo-bolt-gen-v05",
  "description": "Advanced bolt generation tool...",
  "vendor": "The Well Tarot",
  "product_type": "Blender Add-on",
  "tags": ["blender", "addon", "modeling"],
  "status": "active",
  "variants": [
    {
      "price": "0.00",
      "sku": "NO3D-TOOLS-DOJO-BOLT-GEN-V05",
      "inventory_policy": "continue",
      "inventory_management": "shopify"
    }
  ],
  "metafields": [
    {
      "namespace": "no3d_tools",
      "key": "asset_type",
      "value": "Blender Add-on",
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
      "value": "2024-10-24",
      "type": "date"
    }
  ]
}
```

### Shopify Integration Features

- **Product Fields**: Standard Shopify product structure with title, handle, description, vendor, product_type, tags, and status
- **Variants**: Automatic SKU generation with NO3D-TOOLS prefix
- **Metafields**: Rich metadata stored in Shopify metafields with proper namespacing
- **Asset Metadata**: Blender version, export date, geometry stats, and custom properties
- **File References**: Blend file and thumbnail paths for easy asset management

## Requirements

- Blender 4.5 or later
- Assets must be marked as assets in the Asset Browser
- Write permissions to the target directory

## Troubleshooting

- **No assets found**: Make sure your objects/materials are marked as assets in the Asset Browser (Right-click object > Mark as Asset)
- **Export errors**: Check that you have write permissions to the target directory
- **Missing thumbnails**: Some assets may not have preview images generated yet
- **AttributeError after updating**: Restart Blender to clear cached Python modules
- **Properties not showing**: Make sure you removed the old version completely before installing the new one

### Known Limitations

Due to Blender 4.5 Asset Browser API limitations:
- Cannot detect individually selected assets in Asset Browser (exports all assets in file)
- Cannot access assets from external Asset Libraries directly (must open source .blend file)

## Development

This add-on is built using the Blender Python API and follows Blender add-on development conventions.

### Key Components

- `__init__.py`: Add-on registration and metadata
- `operators.py`: Export operators with directory picker
- `ui.py`: Context menu integration
- `utils.py`: Helper functions for export logic

## License

This add-on is provided as-is for use with Blender 4.5+.
