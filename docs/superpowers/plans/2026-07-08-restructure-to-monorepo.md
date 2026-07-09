# Step 1 — Restructure to No3d Dev Monorepo (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Design spec:** `docs/superpowers/specs/2026-07-08-no3d-dev-monorepo-design.md`
— read that first for the "why". This is the "how" for Step 1 only.

**Goal:** Convert the repo from "single-extension with subpackages" to
"monorepo containing N independent extensions", with `no3d_asset_developer` as
the first (and initially only) sub-add-on. No behavioral change to what
`no3d_asset_developer` does or how it registers — just where its files live
and how the tooling finds them.

**Architecture:** After Step 1, `extensions/no3d_asset_developer/` contains
everything that used to live at the repo root (with `save_reload/` and
`claude_pair/` still merged inside it as subpackages — those unmerge in Steps
4–5). `tools/*.sh` iterate over `extensions/*/`. GitHub repo renamed to
`no3d-dev`. gh-pages URL migrated. Both Macs manually resubscribe (per spec:
Option B, two clicks each).

**Tech Stack:** Blender 5.x extension API, extension manifest format, headless
Blender CLI. Bash for tooling.

## Global Constraints

- **Blender floor:** `blender_version_min = "5.0.0"` stays.
- **Extension id continuity:** `no3d_asset_developer` keeps its id exactly.
  Prefs, keymaps, and user Assets Browser entries continue to work across the
  restructure.
- **Version bump:** Bump `no3d_asset_developer` to `4.0.0` in the extension's
  manifest AND `__init__.py` bl_info. Major bump signals the URL change to
  anyone tracking release history. **Both files must match.**
- **Repo rename lands BEFORE the code move commit** so the GitHub redirect
  from `no3d-asset-developer` → `no3d-dev` is in place for the whole diff.
- **URL migration is Option B** (manual resubscribe on both Macs). No bridge
  release.
- **Verification assertions:** apply the same discipline from the current
  AGENTS.md:
  - AddonPreferences → use `is_registered`, never `hasattr(bpy.types, ...)`
  - Prefs props → read from `<PrefsClass>.bl_rna.properties`, not
    `bpy.context.preferences.addons[...]`
  - `--factory-startup` + only-the-extension-under-test for headless runs
- **`${BLENDER:-…}`** honored in every shell script.

## Source-of-truth paths (before → after)

- Repo root: `/Users/joebowers/Projects/no3d-asset-developer` — stays at this
  local path even after the GitHub rename (git remote URL updates, working
  dir doesn't move).
- Current source files at repo root → move to
  `extensions/no3d_asset_developer/`.
- Repo `no3d-asset-developer` (GitHub) → renamed to `no3d-dev`.
- gh-pages URL `node-dojo.github.io/no3d-asset-developer/index.json` →
  `node-dojo.github.io/no3d-dev/index.json`.

## File structure (what this plan creates/modifies/moves)

```
no3d-dev/                                  # renamed GitHub repo; local dir unchanged
├── extensions/
│   └── no3d_asset_developer/              # NEW dir; current root files move here
│       ├── blender_manifest.toml          # MOVED, version bumped to 4.0.0
│       ├── __init__.py                    # MOVED, bl_info bumped to 4.0.0
│       ├── operators.py                   # MOVED
│       ├── ui.py                          # MOVED
│       ├── utils.py                       # MOVED
│       ├── ... (all other current files)  # MOVED
│       ├── wip/                           # MOVED (subpackage of this extension)
│       ├── notes/                         # MOVED
│       ├── save_reload/                   # MOVED (still merged for now)
│       ├── claude_pair/                   # MOVED
│       ├── extraction_methods.py          # MOVED
│       ├── blend_export.py                # MOVED
│       ├── _export_single_asset.py        # MOVED
│       ├── _export_template.blend         # MOVED
│       └── repo_registration.py           # MOVED, URL updated to new gh-pages
├── tools/
│   ├── build_all.sh                       # NEW
│   ├── publish_repo.sh                    # UPDATED (iterates via build_all)
│   └── check_register.sh                  # UPDATED (iterates extensions/*/)
├── docs/superpowers/{specs,plans}/        # unchanged location
├── .superpowers/sdd/                      # unchanged location
├── AGENTS.md                              # REWRITTEN for monorepo shape
└── README.md                              # REWRITTEN for monorepo shape
```

## Non-move files (stay at repo root)

- `AGENTS.md` (rewritten)
- `README.md` (rewritten)
- `tools/`
- `docs/`
- `.superpowers/`
- `.gitignore`
- `LICENSE`
- `.git/` (obviously)

Everything else at the current repo root moves.

---

### Task 0: Verification harness for the monorepo shape

Rewrite `tools/check_register.sh` to iterate over `extensions/*/` and validate
each sub-extension. Before Task 1 moves files, this new script won't find any
extensions dir — that's expected. Prove it works after Task 1's move.

**Files:**
- Modify: `tools/check_register.sh`

**Interfaces:**
- Produces: `tools/check_register.sh` exits 0 and prints `REGISTER_OK` when all
  extensions in `extensions/*/` register + unregister cleanly. Non-zero + trace
  on first failure. Takes no args.

- [ ] **Step 1: Rewrite `tools/check_register.sh`**

```bash
#!/bin/bash
# check_register.sh — headless proof that every extension in extensions/*/
# registers and unregisters cleanly. Uses --factory-startup so the user's
# normal add-ons don't come along (headless + user add-ons often hangs).
#
# Usage:  tools/check_register.sh                # all extensions
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
  targets=("$EXT_ROOT/$1")
else
  targets=("$EXT_ROOT"/*/)
fi

for ext_dir in "${targets[@]}"; do
  ext_name="$(basename "$ext_dir")"
  echo "==> Checking $ext_name"
  "$BLENDER" --factory-startup --background --python-expr "
import bpy, sys, traceback
EXT_DIR = r'''${ext_dir%/}'''
EXT_NAME = r'''$ext_name'''
try:
    # Extension dirs are already underscore-safe by convention — no symlink
    # shim needed at this level (the hyphenated *outer* repo dir is not on
    # sys.path).
    import os
    parent = os.path.dirname(EXT_DIR)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    mod = __import__(EXT_NAME)
    mod.register()
    # Find the AddonPreferences subclass on the module and assert
    # is_registered (AddonPreferences classes are NOT exposed on bpy.types).
    from bpy.types import AddonPreferences
    prefs_cls = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and issubclass(obj, AddonPreferences) and obj is not AddonPreferences:
            prefs_cls = obj
            break
    if prefs_cls is None:
        # Some extensions may not define AddonPreferences — skip the assertion.
        pass
    else:
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
```

- [ ] **Step 2: Make executable + smoke-test against the empty state**

```bash
chmod +x tools/check_register.sh
tools/check_register.sh 2>&1 | tail -5
```

Expected on the pre-Task-1 tree: exits 1 with
`ERROR: … extensions … does not exist`. That's the correct pre-restructure
signal — the harness works.

- [ ] **Step 3: Commit (do not push yet — Task 1 will land as a batch)**

```bash
git add tools/check_register.sh
git commit -m "tools: multi-extension register-check for the monorepo shape

Iterates extensions/*/, symlink-free import (dirs are underscore-safe),
--factory-startup + register-only-target discipline. Finds AddonPreferences
via subclass scan; falls back to skip if an extension doesn't define one.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 1: Move current source into `extensions/no3d_asset_developer/`

Big commit, but mechanically simple: `git mv` every current root file into
the new nested location, update `repo_registration.py`'s URL, bump versions,
and prove the harness passes.

**Files:**
- Create: `extensions/no3d_asset_developer/` (via git mv)
- Modify: `extensions/no3d_asset_developer/blender_manifest.toml` (version 3.2.0 → 4.0.0)
- Modify: `extensions/no3d_asset_developer/__init__.py` (bl_info version)
- Modify: `extensions/no3d_asset_developer/repo_registration.py` (URL)

- [ ] **Step 1: `git mv` every non-tooling / non-docs file into the new location**

```bash
mkdir -p extensions/no3d_asset_developer
# Everything that's currently code / manifests / notes / _export_template goes.
# Stay at repo root: tools/, docs/, .superpowers/, README.md, AGENTS.md,
# LICENSE, .gitignore.
for f in __init__.py operators.py ui.py utils.py \
         extraction_methods.py blend_export.py _export_single_asset.py \
         _export_template.blend blender_manifest.toml \
         repo_registration.py wip_sync.py aspect_overlay.py \
         clipboard_paste.py editor_screenshot.py header_screenshots.py \
         node_screenshot.py viewport_format.py viewport_screenshot.py \
         demo_catalog_selection.py test_shopify_json.py test_shopify_output.json \
         CATALOG_SELECTION_README.md V2_PLAN.md _create_template.py \
         "Bracket Gen 4.5_node_group_ascii.txt" "ascii nodes" \
         "nodetools banner 1.png"; do
  if [ -e "$f" ]; then
    git mv "$f" "extensions/no3d_asset_developer/$f"
  fi
done
git mv wip extensions/no3d_asset_developer/wip
git mv notes extensions/no3d_asset_developer/notes
git mv save_reload extensions/no3d_asset_developer/save_reload
git mv claude_pair extensions/no3d_asset_developer/claude_pair
# dist/ and no3d_asset_developer-*.zip are gitignored — leave alone.
```

Sanity check nothing important was left behind:

```bash
ls -1 | grep -Ev '^(AGENTS\.md|README\.md|LICENSE|tools|docs|dist|\.superpowers|\.gitignore|extensions|\.git|\.DS_Store|__pycache__)$'
```

Expected: empty output. If anything appears, decide (move or leave) before
continuing.

- [ ] **Step 2: Bump the version in both places**

Edit `extensions/no3d_asset_developer/blender_manifest.toml`:
```toml
version = "4.0.0"
```

Edit `extensions/no3d_asset_developer/__init__.py`:
```python
"version": (4, 0, 0),
```

- [ ] **Step 3: Update the gh-pages URL in `repo_registration.py`**

In `extensions/no3d_asset_developer/repo_registration.py`, change the
subscription URL from
`https://node-dojo.github.io/no3d-asset-developer/index.json` to
`https://node-dojo.github.io/no3d-dev/index.json`.

The Blender-side "add repo" call takes both URL and display name — set the
display name to `"No3d Dev"` to match the new umbrella naming.

- [ ] **Step 4: Rename the GitHub repo**

On github.com/node-dojo/no3d-asset-developer → Settings → Rename to `no3d-dev`.
GitHub sets up automatic redirects for the old URL, so `git push` etc. keep
working. Verify:

```bash
git remote -v
git remote set-url origin https://github.com/node-dojo/no3d-dev.git
git remote -v
```

(GitHub also honors pushes to the old URL for a while, but pin the new URL
now.)

- [ ] **Step 5: Run the multi-extension register-check**

```bash
tools/check_register.sh 2>&1 | tail -10
```

Expected: `no3d_asset_developer_OK` then `REGISTER_OK`.

If this fails, the most likely cause is a stale `__pycache__` in the moved
tree confusing the import. Clear it:

```bash
find extensions -type d -name __pycache__ -exec rm -rf {} +
tools/check_register.sh 2>&1 | tail -10
```

- [ ] **Step 6: Commit the move**

```bash
git add -A
git commit -m "restructure: move no3d_asset_developer into extensions/ (monorepo shape)

Preparing the repo for multiple sub-add-ons (Agent Bridge next). No
behavioral change to no3d_asset_developer itself — it just lives at
extensions/no3d_asset_developer/ now and is bumped to 4.0.0 to signal the
extension-repo URL migration (node-dojo.github.io/no3d-dev/index.json).

repo_registration.py updated to point at the new URL and use \"No3d Dev\"
as the display name.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Rewrite `tools/publish_repo.sh` for the multi-extension shape

Iterate `extensions/*/` (or take a `--only <name>` arg for single-extension
republishes), build each, aggregate into the scratch repo dir, generate the
index, force-push to gh-pages under the new URL.

**Files:**
- Create: `tools/build_all.sh`
- Modify: `tools/publish_repo.sh`

- [ ] **Step 1: Create `tools/build_all.sh`**

```bash
#!/bin/bash
# build_all.sh — build every extension in extensions/*/ into dist/.
#
# Usage:  tools/build_all.sh [ext_name ...]   # all if no args
# Env:    BLENDER (path to Blender binary)
set -euo pipefail

BLENDER="${BLENDER:-/Applications/Blender 5.2 Beta.app/Contents/MacOS/Blender}"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
EXT_ROOT="$PROJECT/extensions"
DIST="$PROJECT/dist"
mkdir -p "$DIST"

if [ $# -gt 0 ]; then
  targets=()
  for name in "$@"; do targets+=("$EXT_ROOT/$name/"); done
else
  targets=("$EXT_ROOT"/*/)
fi

for ext_dir in "${targets[@]}"; do
  ext_name="$(basename "$ext_dir")"
  version=$(grep '^version' "$ext_dir/blender_manifest.toml" | head -1 | cut -d'"' -f2)
  zip_name="${ext_name}-${version}.zip"
  echo "==> Building $zip_name"
  "$BLENDER" --factory-startup --command extension build \
    --source-dir "$ext_dir" --output-filepath "$DIST/$zip_name"
done
```

`chmod +x tools/build_all.sh`.

- [ ] **Step 2: Rewrite `tools/publish_repo.sh` to consume `build_all`**

```bash
#!/bin/bash
# publish_repo.sh — build every extension, assemble the static repo dir,
# generate index.json + html landing, force-push to gh-pages.
#
# Result: https://node-dojo.github.io/no3d-dev/index.json
#
# Usage:  tools/publish_repo.sh
# Env:    BLENDER (path to Blender binary)
set -euo pipefail

BLENDER="${BLENDER:-/Applications/Blender 5.2 Beta.app/Contents/MacOS/Blender}"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$HOME/.no3d-extension-repo"
DIST="$PROJECT/dist"

echo "==> Building all extensions"
"$PROJECT/tools/build_all.sh"

echo "==> Assembling repo dir at $REPO_DIR"
mkdir -p "$REPO_DIR"
# Keep prior zips; new versions are additive. server-generate picks up all.
cp -f "$DIST"/*.zip "$REPO_DIR/"

echo "==> Generating index.json (+ html landing)"
"$BLENDER" --factory-startup --command extension server-generate \
  --repo-dir "$REPO_DIR" --html

echo "==> Publishing to gh-pages"
cd "$REPO_DIR"
if [ ! -d .git ]; then
  git init -b gh-pages
  git remote add origin https://github.com/node-dojo/no3d-dev.git
else
  # Update the remote in case the scratch repo was set up under the old name.
  git remote set-url origin https://github.com/node-dojo/no3d-dev.git
fi
touch .nojekyll
git add -A
git commit -m "repo: publish extensions" || echo "(nothing to commit)"
git push -f origin gh-pages

echo ""
echo "Done. Repo URL:"
echo "  https://node-dojo.github.io/no3d-dev/index.json"
```

- [ ] **Step 3: Dry-run — build only, don't publish**

```bash
tools/build_all.sh 2>&1 | tail -10
ls -lh dist/
```

Expected: `dist/no3d_asset_developer-4.0.0.zip` present, sane size (should
be within 10% of the existing 3.2.0 zip).

- [ ] **Step 4: Real publish**

```bash
tools/publish_repo.sh 2>&1 | tail -20
```

Expected: ends with the "Done. Repo URL" line. Visit
`https://node-dojo.github.io/no3d-dev/index.json` in a browser to confirm
the JSON lists `no3d_asset_developer 4.0.0`.

- [ ] **Step 5: Commit**

```bash
git add tools/build_all.sh tools/publish_repo.sh
git commit -m "tools: publish pipeline iterates extensions/*/

build_all.sh builds every sub-add-on into dist/. publish_repo.sh consumes
dist/*.zip, assembles the static repo dir, runs extension server-generate
--html, force-pushes to the renamed no3d-dev gh-pages branch. gh-pages URL
migrates to https://node-dojo.github.io/no3d-dev/index.json.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Rewrite `AGENTS.md` and `README.md` for the monorepo shape

The current AGENTS.md was written for the single-add-on-with-subpackages
shape. Rewrite the sections that don't survive the transition; keep
everything that still applies verbatim.

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`

- [ ] **Step 1: AGENTS.md — surgical rewrites**

Rewrite these sections (leave the rest of the file — Cowork specifics,
workflow, Lessons/gotchas — as-is):

- **"What this is"** — now: "No3d Dev is a monorepo of independent Blender
  extensions. `extensions/<name>/` per extension. `tools/*.sh` iterate.
  Distributed as a self-hosted extension repository at
  `node-dojo.github.io/no3d-dev/index.json`."
- **"Non-negotiables"** — replace "One AddonPreferences for the whole
  add-on" with "One AddonPreferences per sub-add-on". Drop the
  `HOST_PACKAGE = __package__.rsplit(".", 1)[0]` rule (no longer needed).
  Add "No cross-extension Python imports; use `bpy.ops` calls instead."
- **"Blender quirks / gotchas"** — the "hyphenated repo dir isn't
  importable" note applies to the *outer* repo only; extension dirs are
  underscore-safe by convention. Reword to reflect that.
- **"Directory map"** — replace with the extensions/*/ layout from the spec.
- Add a new **"Cross-extension conventions"** section mirroring the spec:
  `NO3D_<PREFIX>_*` classname prefixes, `bpy.ops.<name>` for cross-extension
  calls, shared-code discipline.

- [ ] **Step 2: README.md — user-facing rewrite**

Rewrite to reflect the monorepo:
- What is No3d Dev (collection of extensions)
- How to subscribe in Blender (the new URL)
- List of extensions currently in the repo (initially just
  `no3d_asset_developer`)
- Development section pointing at AGENTS.md for contributor / agent onboarding

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md README.md
git commit -m "docs: AGENTS.md + README.md rewritten for the monorepo shape

Drops the single-AddonPreferences / HOST_PACKAGE rules (per-sub-add-on now);
adds cross-extension conventions (classname prefixes, bpy.ops calls, no
python imports across extensions). README points users at the new
no3d-dev/index.json URL.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Push to origin + manual URL resubscribe on both Macs

**Files:** none (git + Blender-side action).

- [ ] **Step 1: Push everything**

```bash
git log --oneline origin/main..HEAD    # sanity-check the batch
git push origin main
```

- [ ] **Step 2: Resubscribe on the home Mac**

In Blender → Edit → Preferences → Get Extensions → Repositories → find the
old `node-dojo.github.io/no3d-asset-developer/index.json` entry → change
URL to `node-dojo.github.io/no3d-dev/index.json` → refresh. Confirm the
new `no3d_asset_developer 4.0.0` shows up and updates cleanly from 3.2.0.

- [ ] **Step 3: Resubscribe on the work Mac**

Same steps. This is the migration Option B trade-off — two clicks each,
one-time.

- [ ] **Step 4: Verify the old URL can be retired**

Leave the old URL alone for now (still works via gh-pages redirect from
the renamed repo). Delete the old subscription entries after both Macs
confirm they're pulling from the new URL. In a future ship, retire the
old gh-pages branch entirely if desired.

- [ ] **Step 5: Report the pushed range + confirmation from both Macs**

Note the top commit SHA and confirm in the task report that both Macs
have installed `no3d_asset_developer 4.0.0` from the new URL.

---

## Self-Review

**Spec coverage** (against `2026-07-08-no3d-dev-monorepo-design.md`):
- New structure `extensions/no3d_asset_developer/` → Task 1. ✓
- URL migration (Option B) → Task 4. ✓
- `tools/build_all.sh` new + `publish_repo.sh` updated → Task 2. ✓
- `tools/check_register.sh` iterates → Task 0. ✓
- Version bump (both places) to 4.0.0 → Task 1. ✓
- `repo_registration.py` URL updated → Task 1 Step 3. ✓
- AGENTS.md rewritten for monorepo shape → Task 3. ✓
- Cross-extension conventions section added to AGENTS.md → Task 3. ✓
- Blender floor unchanged → Global Constraints. ✓
- Steps 2–5 (Agent Bridge, ship.sh, unmerges) explicitly deferred → spec's
  phased plan. ✓

**Placeholder scan:** No TBD/TODO. Every code step shows full code; every
verify step shows the exact command + expected output.

**Known risk flagged for the executor:**
- The GitHub repo rename must happen before the code-move commit lands
  (Task 1 Step 4 vs Step 6). If Step 4 is skipped, the `git push` in Task 4
  works via redirect but the local `git remote -v` will still say
  `no3d-asset-developer`, confusing future agents. Do them in order.
- If Blender's Get Extensions on either Mac has cached the old URL's index,
  a hard "Check for Updates" is required after the URL swap. Documented in
  Task 4 Steps 2–3.
- The move commit in Task 1 Step 6 is intentionally large but purely
  positional — no diff inside any moved file except the manifest / bl_info
  version bump and the `repo_registration.py` URL. Reviewers should see
  100% renames + 2 tiny edits.
