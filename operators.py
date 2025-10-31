import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty
from . import utils


# Define asset type enum items as a constant
ASSET_TYPE_ITEMS = [
    ('ALL', 'All Types', 'Export all asset types'),
    ('OBJECT', 'Objects', 'Export object assets only'),
    ('MATERIAL', 'Materials', 'Export material assets only'),
    ('COLLECTION', 'Collections', 'Export collection assets only'),
    ('NODE_TREE', 'Node Groups', 'Export node group assets only'),
]

# Define catalog selection enum items
def get_catalog_items(self, context):
    """Dynamic enum for catalog selection."""
    catalogs = utils.get_available_catalogs()
    items = [('ALL_CATALOGS', 'All Catalogs', 'Export assets from all catalogs (excluding unassigned)')]
    items.extend([(catalog, catalog, f'Export assets from {catalog} catalog') for catalog in catalogs])
    return items


class NO3D_OT_export_selected_assets(Operator):
    """Export all assets with metadata and thumbnails (Asset Browser API limitation: cannot detect individual selection)"""
    bl_idname = "asset.export_selected_no3d"
    bl_label = "Export All Assets (Quick)"
    bl_description = "Export all assets from current .blend file. Note: Due to Blender Asset Browser API limitations, individual selection is not available."
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties
    directory: StringProperty(
        name="Export Directory",
        description="Directory to export assets to",
        subtype='DIR_PATH',
        default=""
    )
    
    export_json: BoolProperty(
        name="Export JSON Metadata",
        description="Generate JSON metadata files for each asset",
        default=True
    )
    
    export_thumbnail: BoolProperty(
        name="Export Thumbnails",
        description="Export PNG thumbnails for each asset",
        default=True
    )
    
    export_markdown: BoolProperty(
        name="Export Markdown Description",
        description="Generate markdown description files for each asset",
        default=True
    )
    
    def invoke(self, context, event):
        """Invoke file browser for directory selection"""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        """Execute the export operation"""
        if not self.directory:
            self.report({'ERROR'}, "No directory selected")
            return {'CANCELLED'}
        
        # Get selected assets
        selected_assets = utils.get_selected_assets(context)
        catalog_name = "Default"  # Default catalog for selected assets
        
        print(f"NO3D Export: Found {len(selected_assets)} assets")
        for asset in selected_assets:
            print(f"  - {asset.name} ({type(asset).__name__})")
        
        if not selected_assets:
            self.report({'WARNING'}, "No assets found in current .blend file. Make sure objects/materials are marked as assets.")
            return {'CANCELLED'}
        
        # Create export directory if it doesn't exist
        os.makedirs(self.directory, exist_ok=True)
        
        # Progress reporting
        wm = context.window_manager
        wm.progress_begin(0, len(selected_assets))
        
        exported_count = 0
        errors = []
        
        try:
            for i, asset in enumerate(selected_assets):
                wm.progress_update(i)
                
                try:
                    # Export .blend file
                    blend_path = utils.export_asset_blend(asset, self.directory)
                    if blend_path:
                        exported_count += 1
                    
                    # Export JSON metadata
                    if self.export_json:
                        utils.generate_asset_json(asset, self.directory, catalog_name)
                    
                    # Export thumbnail
                    if self.export_thumbnail:
                        utils.export_asset_thumbnail(asset, self.directory)
                    
                    # Export markdown description
                    if self.export_markdown:
                        utils.generate_asset_markdown(asset, self.directory, catalog_name)
                        
                except Exception as e:
                    errors.append(f"Error exporting {getattr(asset, 'name', 'unknown')}: {str(e)}")
        
        finally:
            wm.progress_end()
        
        # Report results
        if errors:
            self.report({'WARNING'}, f"Exported {exported_count} assets with {len(errors)} errors")
            for error in errors:
                print(f"Export error: {error}")
        else:
            self.report({'INFO'}, f"Successfully exported {exported_count} assets")
        
        return {'FINISHED'}


class NO3D_OT_export_all_assets(Operator):
    """Export all visible assets with metadata and thumbnails"""
    bl_idname = "asset.export_all_no3d"
    bl_label = "Export All Assets"
    bl_description = "Export all assets from current .blend file as individual .blend files with JSON metadata and thumbnails"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties
    directory: StringProperty(
        name="Export Directory",
        description="Directory to export assets to",
        subtype='DIR_PATH',
        default=""
    )
    
    asset_type_filter: EnumProperty(
        name="Asset Type",
        description="Filter which asset types to export",
        items=ASSET_TYPE_ITEMS,
        default='ALL'
    )
    
    catalog_filter: EnumProperty(
        name="Catalog",
        description="Select which catalog to export from",
        items=get_catalog_items,
        default='ALL_CATALOGS'
    )
    
    export_json: BoolProperty(
        name="Export JSON Metadata",
        description="Generate JSON metadata files for each asset",
        default=True
    )
    
    export_thumbnail: BoolProperty(
        name="Export Thumbnails",
        description="Export PNG thumbnails for each asset",
        default=True
    )
    
    export_markdown: BoolProperty(
        name="Export Markdown Description",
        description="Generate markdown description files for each asset",
        default=True
    )
    
    def draw(self, context):
        """Draw the file browser options"""
        layout = self.layout
        layout.prop(self, "asset_type_filter")
        layout.prop(self, "catalog_filter")
        layout.prop(self, "export_json")
        layout.prop(self, "export_thumbnail")
        layout.prop(self, "export_markdown")
    
    def invoke(self, context, event):
        """Invoke file browser for directory selection"""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        """Execute the export operation"""
        if not self.directory:
            self.report({'ERROR'}, "No directory selected")
            return {'CANCELLED'}
        
        # Get assets based on catalog filter
        if self.catalog_filter == 'ALL_CATALOGS':
            all_assets = utils.get_all_visible_assets(context, self.asset_type_filter)
            catalog_name = "All Catalogs"
        else:
            all_assets = utils.get_assets_by_catalog(self.catalog_filter, self.asset_type_filter)
            catalog_name = self.catalog_filter
        
        print(f"\n{'='*60}")
        print(f"NO3D Export: Searching for assets in current .blend file")
        print(f"Asset Type Filter: {self.asset_type_filter}")
        print(f"Catalog Filter: {self.catalog_filter}")
        print(f"Found {len(all_assets)} assets")
        print(f"{'='*60}")
        
        for asset in all_assets:
            asset_type = type(asset).__name__
            has_asset_data = hasattr(asset, 'asset_data') and asset.asset_data is not None
            print(f"  - {asset.name} ({asset_type}) - Asset Data: {has_asset_data}")
        
        if not all_assets:
            self.report({'ERROR'}, "No assets found in current .blend file. Please mark objects/materials/collections as assets first (Right-click > Mark as Asset)")
            print("\nDEBUG INFO:")
            print(f"Total objects in file: {len(bpy.data.objects)}")
            print(f"Total materials in file: {len(bpy.data.materials)}")
            print(f"Total collections in file: {len(bpy.data.collections)}")
            return {'CANCELLED'}
        
        # Create export directory if it doesn't exist
        os.makedirs(self.directory, exist_ok=True)
        
        # Progress reporting
        wm = context.window_manager
        wm.progress_begin(0, len(all_assets))
        
        exported_count = 0
        errors = []
        
        try:
            for i, asset in enumerate(all_assets):
                wm.progress_update(i)
                
                try:
                    # Export .blend file
                    blend_path = utils.export_asset_blend(asset, self.directory)
                    if blend_path:
                        exported_count += 1
                    
                    # Export JSON metadata
                    if self.export_json:
                        utils.generate_asset_json(asset, self.directory, catalog_name)
                    
                    # Export thumbnail
                    if self.export_thumbnail:
                        utils.export_asset_thumbnail(asset, self.directory)
                    
                    # Export markdown description
                    if self.export_markdown:
                        utils.generate_asset_markdown(asset, self.directory, catalog_name)
                        
                except Exception as e:
                    errors.append(f"Error exporting {getattr(asset, 'name', 'unknown')}: {str(e)}")
        
        finally:
            wm.progress_end()
        
        # Report results
        if errors:
            self.report({'WARNING'}, f"Exported {exported_count} assets with {len(errors)} errors")
            for error in errors:
                print(f"Export error: {error}")
        else:
            self.report({'INFO'}, f"Successfully exported {exported_count} assets")
        
        return {'FINISHED'}


class NO3D_OT_export_thumbnails_only(Operator):
    """Export only thumbnail images for all assets"""
    bl_idname = "asset.export_thumbnails_only_no3d"
    bl_label = "Export Thumbnails Only"
    bl_description = "Export only thumbnail/icon images for all assets in current .blend file"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Properties
    directory: StringProperty(
        name="Export Directory",
        description="Directory to export thumbnails to",
        subtype='DIR_PATH',
        default=""
    )
    
    asset_type_filter: EnumProperty(
        name="Asset Type",
        description="Filter which asset types to export",
        items=ASSET_TYPE_ITEMS,
        default='ALL'
    )
    
    catalog_filter: EnumProperty(
        name="Catalog",
        description="Select which catalog to export from",
        items=get_catalog_items,
        default='ALL_CATALOGS'
    )
    
    def draw(self, context):
        """Draw the file browser options"""
        layout = self.layout
        layout.prop(self, "asset_type_filter")
        layout.prop(self, "catalog_filter")
    
    def invoke(self, context, event):
        """Invoke file browser for directory selection"""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        """Execute the thumbnail export operation"""
        if not self.directory:
            self.report({'ERROR'}, "No directory selected")
            return {'CANCELLED'}
        
        # Get assets based on catalog filter
        if self.catalog_filter == 'ALL_CATALOGS':
            all_assets = utils.get_all_visible_assets(context, self.asset_type_filter)
            catalog_name = "All Catalogs"
        else:
            all_assets = utils.get_assets_by_catalog(self.catalog_filter, self.asset_type_filter)
            catalog_name = self.catalog_filter
        
        print(f"\n{'='*60}")
        print(f"NO3D Thumbnail Export: Searching for assets")
        print(f"Asset Type Filter: {self.asset_type_filter}")
        print(f"Catalog Filter: {self.catalog_filter}")
        print(f"Found {len(all_assets)} assets")
        print(f"{'='*60}")
        
        if not all_assets:
            self.report({'ERROR'}, "No assets found in current .blend file")
            return {'CANCELLED'}
        
        # Create export directory if it doesn't exist
        os.makedirs(self.directory, exist_ok=True)
        
        # Progress reporting
        wm = context.window_manager
        wm.progress_begin(0, len(all_assets))
        
        exported_count = 0
        errors = []
        
        try:
            for i, asset in enumerate(all_assets):
                wm.progress_update(i)
                
                try:
                    # Export thumbnail only
                    thumbnail_path = utils.export_asset_thumbnail(asset, self.directory)
                    if thumbnail_path:
                        exported_count += 1
                        
                except Exception as e:
                    errors.append(f"Error exporting thumbnail for {getattr(asset, 'name', 'unknown')}: {str(e)}")
        
        finally:
            wm.progress_end()
        
        # Report results
        if errors:
            self.report({'WARNING'}, f"Exported {exported_count} thumbnails with {len(errors)} errors")
            for error in errors:
                print(f"Export error: {error}")
        else:
            self.report({'INFO'}, f"Successfully exported {exported_count} thumbnails")
        
        return {'FINISHED'}


def register():
    bpy.utils.register_class(NO3D_OT_export_selected_assets)
    bpy.utils.register_class(NO3D_OT_export_all_assets)
    bpy.utils.register_class(NO3D_OT_export_thumbnails_only)


def unregister():
    bpy.utils.unregister_class(NO3D_OT_export_thumbnails_only)
    bpy.utils.unregister_class(NO3D_OT_export_all_assets)
    bpy.utils.unregister_class(NO3D_OT_export_selected_assets)
