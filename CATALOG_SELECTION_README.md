# NO3D Tools Asset Utility - Catalog Selection Feature

## Overview

This branch adds catalog selection functionality to the NO3D Tools Asset Utility, allowing users to specify which catalog should be exported. When a catalog is selected, only the assets in that catalog are exported, and the catalog name is written to the exported JSON files.

## New Features

### 1. Catalog Selection Dropdown
- Added a "Catalog" dropdown to both export operators (Full Export and Thumbnails Only)
- Options include:
  - **All Catalogs**: Export assets from all catalogs (excluding unassigned)
  - **Individual Catalogs**: Export assets from specific catalogs only
  - **Local File Catalogs**: Export assets from the current .blend file

### 2. Catalog Filtering Logic
- New `get_available_catalogs()` function to detect available catalogs
- New `get_assets_by_catalog()` function to filter assets by catalog
- Enhanced asset filtering to respect catalog selection

### 3. Catalog Metadata in JSON
- Added `catalog_name` metafield to exported JSON files
- Catalog information is stored in the `no3d_tools` namespace
- Helps track which catalog each asset belongs to

## Usage

### Export All Catalogs
1. Select "All Catalogs" from the Catalog dropdown
2. Choose your asset type filter (All Types, Objects, Materials, etc.)
3. Click "Export All Assets" or "Export All Thumbnails"
4. All assets from all catalogs will be exported (excluding unassigned)

### Export Specific Catalog
1. Select a specific catalog from the Catalog dropdown
2. Choose your asset type filter
3. Click "Export All Assets" or "Export All Thumbnails"
4. Only assets from the selected catalog will be exported

### Export Local File Assets
1. Select "Local File Catalogs" from the Catalog dropdown
2. Choose your asset type filter
3. Click "Export All Assets" or "Export All Thumbnails"
4. Assets from the current .blend file will be exported

## JSON Output Changes

The exported JSON files now include catalog information in the metafields:

```json
{
  "metafields": [
    {
      "namespace": "no3d_tools",
      "key": "catalog_name",
      "value": "Test Catalog",
      "type": "single_line_text_field"
    }
  ]
}
```

## Technical Implementation

### New Functions in `utils.py`
- `get_available_catalogs()`: Returns list of available catalogs
- `get_assets_by_catalog(catalog_name, asset_type_filter)`: Filters assets by catalog
- `generate_asset_json(asset, target_dir, catalog_name)`: Updated to include catalog name

### Updated Operators in `operators.py`
- Added `catalog_filter` property to both export operators
- Added `get_catalog_items()` function for dynamic enum generation
- Updated execute methods to use catalog filtering

### UI Updates in `ui.py`
- Added catalog selection information to the panel
- Updated operator draw methods to show catalog dropdown

## Testing

The functionality has been tested with the included test script:

```bash
python3 test_shopify_json.py
```

This generates a sample JSON output showing the catalog information in the metafields.

## Installation

1. Copy the updated files to your Blender add-ons directory
2. Enable the add-on in Blender preferences
3. The catalog selection options will appear in the Asset Browser panel

## Notes

- **Unassigned Assets**: Assets without a catalog assignment are never exported, even when "All Catalogs" is selected
- **Catalog Detection**: The system attempts to detect available catalogs automatically
- **Fallback**: If no catalogs are detected, "Default" is used as a fallback option
- **Compatibility**: This feature is designed for Blender 4.0+ with the new asset system

## Future Enhancements

- Enhanced catalog detection for complex asset library setups
- Support for catalog hierarchies
- Batch catalog assignment tools
- Catalog-specific export settings

## Branch Information

- **Branch**: `catalog-selection-feature`
- **Base**: `master` (original asset utility)
- **Status**: Ready for testing and integration
