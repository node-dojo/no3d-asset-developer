#!/bin/bash
# check_register.sh — headless proof that the add-on enables cleanly and its
# key surfaces are registered. Registers the working tree directly via a
# symlinked import (bypassing Blender's extension install path for speed),
# asserts, tears down.
#
# Uses --factory-startup so the user's normal enabled add-ons do NOT load —
# headless Blender + user add-ons often hangs (modal popups, threads, or
# network calls inside someone's register()). Only this add-on is registered.
#
# Usage:  tools/check_register.sh
# Env:    BLENDER (path to Blender binary; defaults to 5.2 Beta.app)
# Exit 0 + "REGISTER_OK" on success; non-zero + traceback on failure.
set -euo pipefail

BLENDER="${BLENDER:-/Applications/Blender 5.2 Beta.app/Contents/MacOS/Blender}"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"

"$BLENDER" --factory-startup --background --python-expr "
import bpy, sys, traceback
PROJECT = r'''$PROJECT'''
try:
    # The repo dir name (no3d-asset-developer) contains a hyphen, which is
    # not a valid Python module name. Import it via a temp symlink with an
    # underscore name instead.
    import os, tempfile
    tmp = tempfile.mkdtemp()
    link = os.path.join(tmp, 'no3d_asset_developer')
    os.symlink(PROJECT, link)
    if tmp not in sys.path:
        sys.path.insert(0, tmp)
    mod = __import__('no3d_asset_developer')
    mod.register()
    # Assertions: prefs class registered. NOTE: AddonPreferences subclasses
    # are NOT exposed as attributes on bpy.types (confirmed: this is general
    # Blender behavior, reproduced with a throwaway AddonPreferences class
    # outside this add-on — not an add-on bug). cls.is_registered is the
    # correct, robust check for any bpy_struct subclass.
    assert mod.NO3D_AddonPreferences.is_registered, 'host prefs missing'
    mod.unregister()
    assert not mod.NO3D_AddonPreferences.is_registered, 'host prefs still registered after unregister'
    print('REGISTER_OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
"
