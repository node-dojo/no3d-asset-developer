#!/bin/bash
# publish_repo.sh — build every extension in extensions/*/, assemble the
# static repo dir, generate index.json + html landing, force-push to the
# gh-pages branch of the no3d-dev GitHub repo.
#
# Result: https://node-dojo.github.io/no3d-dev/index.json
# Blender users (or Blender installs subscribed via repo_registration.py)
# get native in-Blender updates as soon as gh-pages refreshes.
#
# Usage:  tools/publish_repo.sh
# Env:    BLENDER (path to Blender binary; defaults to 5.2 Beta.app)
# Requires: git authed for node-dojo/no3d-dev.
set -euo pipefail

BLENDER="${BLENDER:-/Applications/Blender 5.2 Beta.app/Contents/MacOS/Blender}"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$HOME/.no3d-extension-repo"     # scratch, outside Dropbox
DIST="$PROJECT/dist"

echo "==> Building all extensions"
"$PROJECT/tools/build_all.sh"

echo "==> Assembling repo dir at $REPO_DIR"
mkdir -p "$REPO_DIR"
# Keep prior zips so older Blender versions can still resolve a compatible
# build; same-version zips are replaced. server-generate picks up all zips
# in the directory and produces a single aggregated index.json.
cp -f "$DIST"/*.zip "$REPO_DIR/"

echo "==> Generating index.json (+ html listing)"
"$BLENDER" --factory-startup --command extension server-generate \
  --repo-dir "$REPO_DIR" --html

echo "==> Publishing to gh-pages"
cd "$REPO_DIR"
if [ ! -d .git ]; then
  git init -b gh-pages
  git remote add origin https://github.com/node-dojo/no3d-dev.git
else
  # Point the scratch repo at the renamed remote in case it was set up
  # against the pre-restructure name.
  git remote set-url origin https://github.com/node-dojo/no3d-dev.git 2>/dev/null || true
fi
touch .nojekyll
git add -A
git commit -m "repo: publish extensions" || echo "(nothing to commit)"
git push -f origin gh-pages

echo ""
echo "Done. Repo URL:"
echo "  https://node-dojo.github.io/no3d-dev/index.json"
