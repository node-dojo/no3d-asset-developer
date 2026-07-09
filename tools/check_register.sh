#!/bin/bash
# check_register.sh — headless proof that every extension in extensions/*/
# registers and unregisters cleanly. Registers each in isolation via a fresh
# --factory-startup Blender launch (headless + user add-ons often hangs, so
# we run with a clean profile and register only the target).
#
# AddonPreferences autodiscovery: scans the extension module's top-level for
# an AddonPreferences subclass and asserts its is_registered. Extensions that
# don't define one are still validated (register/unregister must not raise).
#
# Usage:  tools/check_register.sh                       # all extensions
#         tools/check_register.sh no3d_asset_developer  # one extension
# Env:    BLENDER (path to Blender binary; defaults to 5.2 Beta.app)
# Exit 0 + "REGISTER_OK" on success; non-zero + traceback on first failure.
set -euo pipefail

BLENDER="${BLENDER:-/Applications/Blender 5.2 Beta.app/Contents/MacOS/Blender}"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
EXT_ROOT="$PROJECT/extensions"

if [ ! -d "$EXT_ROOT" ]; then
  echo "ERROR: $EXT_ROOT does not exist. Have you run the restructure yet?" >&2
  exit 1
fi

# If an arg is given, only test that one extension. Otherwise, all.
if [ $# -gt 0 ]; then
  targets=("$EXT_ROOT/$1/")
  if [ ! -d "${targets[0]}" ]; then
    echo "ERROR: extension '$1' not found at ${targets[0]}" >&2
    exit 1
  fi
else
  # Guard against the glob matching literally when no extensions exist yet.
  shopt -s nullglob
  targets=("$EXT_ROOT"/*/)
  shopt -u nullglob
  if [ ${#targets[@]} -eq 0 ]; then
    echo "ERROR: no extensions found under $EXT_ROOT" >&2
    exit 1
  fi
fi

for ext_dir in "${targets[@]}"; do
  ext_name="$(basename "$ext_dir")"
  echo "==> Checking $ext_name"
  "$BLENDER" --factory-startup --background --python-expr "
import bpy, sys, traceback
EXT_DIR = r'''${ext_dir%/}'''
EXT_NAME = r'''$ext_name'''
try:
    # Extension dirs are underscore-safe by convention (no hyphens in names
    # like 'no3d_asset_developer'), so no symlink shim is needed here — the
    # dir name IS the Python module name. The outer repo dir (hyphenated) is
    # never added to sys.path.
    import os
    parent = os.path.dirname(EXT_DIR)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    mod = __import__(EXT_NAME)
    mod.register()
    # AddonPreferences autodiscovery — subclasses are NOT exposed on
    # bpy.types (Blender behavior, reproduced with a throwaway class), so
    # use is_registered on the class directly.
    from bpy.types import AddonPreferences
    prefs_cls = None
    for name in dir(mod):
        obj = getattr(mod, name, None)
        if isinstance(obj, type) and issubclass(obj, AddonPreferences) and obj is not AddonPreferences:
            prefs_cls = obj
            break
    if prefs_cls is not None:
        assert prefs_cls.is_registered, f'{prefs_cls.__name__} not registered after register()'
    mod.unregister()
    if prefs_cls is not None:
        assert not prefs_cls.is_registered, f'{prefs_cls.__name__} still registered after unregister()'
    print(f'{EXT_NAME}_OK')
except Exception:
    traceback.print_exc()
    sys.exit(1)
"
done

echo "REGISTER_OK"
