import bpy
from bpy.types import Menu, Panel


class NO3D_MT_asset_export_menu(Menu):
    """NO3D Export Tools submenu"""
    bl_label = "NO3D Export Tools"
    bl_idname = "NO3D_MT_asset_export_menu"
    
    def draw(self, context):
        layout = self.layout
        
        # Export All Assets (Full) - with options
        layout.operator(
            "asset.export_all_no3d",
            text="Export All Assets",
            icon='EXPORT'
        )
        
        layout.separator()
        
        # Export Thumbnails Only
        layout.operator(
            "asset.export_thumbnails_only_no3d",
            text="Export Thumbnails Only",
            icon='IMAGE_DATA'
        )


class NO3D_PT_asset_export_panel(Panel):
    """NO3D Export Tools panel in Asset Browser"""
    bl_label = "NO3D Export Tools"
    bl_idname = "NO3D_PT_asset_export_panel"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'UI'
    bl_category = "NO3D"
    
    def draw(self, context):
        layout = self.layout
        
        # Full Export Section
        box = layout.box()
        box.label(text="Full Export:", icon='EXPORT')
        box.operator(
            "asset.export_all_no3d",
            text="Export All Assets",
            icon='EXPORT'
        )
        
        # Thumbnails Only Section
        box = layout.box()
        box.label(text="Thumbnails Only:", icon='IMAGE_DATA')
        box.operator(
            "asset.export_thumbnails_only_no3d",
            text="Export All Thumbnails",
            icon='IMAGE_DATA'
        )
        
        # Catalog Selection Info
        box = layout.box()
        box.label(text="Catalog Selection:", icon='ASSET_MANAGER')
        box.label(text="Use the export operators to select", icon='INFO')
        box.label(text="which catalog to export from.")


def draw_asset_browser_context_menu(self, context):
    """Add NO3D export options to Asset Browser context menu"""
    layout = self.layout
    
    # Add separator
    layout.separator()
    
    # Add NO3D Export Tools submenu
    layout.menu("NO3D_MT_asset_export_menu", text="NO3D Export Tools", icon='TOOL_SETTINGS')


def register():
    bpy.utils.register_class(NO3D_MT_asset_export_menu)
    bpy.utils.register_class(NO3D_PT_asset_export_panel)
    
    # Append to Asset Browser context menu - try multiple possible menu names
    try:
        bpy.types.ASSETBROWSER_MT_context_menu.append(draw_asset_browser_context_menu)
    except:
        try:
            bpy.types.ASSETBROWSER_MT_asset.append(draw_asset_browser_context_menu)
        except:
            try:
                bpy.types.ASSETBROWSER_MT_asset_context_menu.append(draw_asset_browser_context_menu)
            except:
                print("NO3D Tools: Could not find Asset Browser context menu to append to")


def unregister():
    try:
        bpy.utils.unregister_class(NO3D_PT_asset_export_panel)
    except:
        pass
    
    try:
        bpy.utils.unregister_class(NO3D_MT_asset_export_menu)
    except:
        pass
    
    # Remove from Asset Browser context menu
    try:
        bpy.types.ASSETBROWSER_MT_context_menu.remove(draw_asset_browser_context_menu)
    except:
        try:
            bpy.types.ASSETBROWSER_MT_asset.remove(draw_asset_browser_context_menu)
        except:
            try:
                bpy.types.ASSETBROWSER_MT_asset_context_menu.remove(draw_asset_browser_context_menu)
            except:
                pass
