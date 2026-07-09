#!/bin/bash
# build_all.sh — build every extension in extensions/*/ into dist/.
#
# For each extensions/<name>/, invokes `blender --command extension build`
# with --source-dir pointing at that extension, producing a versioned zip
# in the top-level dist/ directory. Reads the version from the extension's
# blender_manifest.toml so the zip filename tracks it automatically.
#
# Usage:  tools/build_all.sh                       # build all extensions
#         tools/build_all.sh no3d_asset_developer  # build one extension
# Env:    BLENDER (path to Blender binary; defaults to 5.2 Beta.app)
set -euo pipefail

BLENDER="${BLENDER:-/Applications/Blender 5.2 Beta.app/Contents/MacOS/Blender}"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
EXT_ROOT="$PROJECT/extensions"
DIST="$PROJECT/dist"

if [ ! -d "$EXT_ROOT" ]; then
  echo "ERROR: $EXT_ROOT does not exist." >&2
  exit 1
fi

mkdir -p "$DIST"

if [ $# -gt 0 ]; then
  targets=()
  for name in "$@"; do
    if [ ! -d "$EXT_ROOT/$name" ]; then
      echo "ERROR: extension '$name' not found at $EXT_ROOT/$name" >&2
      exit 1
    fi
    targets+=("$EXT_ROOT/$name/")
  done
else
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
  manifest="$ext_dir/blender_manifest.toml"
  if [ ! -f "$manifest" ]; then
    echo "ERROR: $manifest not found" >&2
    exit 1
  fi
  version=$(grep '^version' "$manifest" | head -1 | cut -d'"' -f2)
  if [ -z "$version" ]; then
    echo "ERROR: could not parse version from $manifest" >&2
    exit 1
  fi
  zip_name="${ext_name}-${version}.zip"
  echo "==> Building $zip_name"
  "$BLENDER" --factory-startup --command extension build \
    --source-dir "$ext_dir" --output-filepath "$DIST/$zip_name"
done

echo "Done. Zips in $DIST:"
ls -1 "$DIST"/*.zip 2>/dev/null || echo "(none)"
