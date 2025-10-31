bl_info = {
    "name": "NO3D Tools Asset Utility",
    "author": "NO3D Tools",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "Asset Browser > Context Menu",
    "description": "Export assets with metadata and thumbnails",
    "category": "Asset",
    "doc_url": "",
    "tracker_url": "",
}

import bpy
from . import operators
from . import ui

def register():
    operators.register()
    ui.register()

def unregister():
    ui.unregister()
    operators.unregister()

if __name__ == "__main__":
    register()
