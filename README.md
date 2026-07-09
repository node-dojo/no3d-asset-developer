# No3d Dev

A monorepo of Blender extensions authored by NO3D Tools, distributed as a
single self-hosted extension repository. One subscription URL in Blender's
Get Extensions gives you every extension below — installable and updatable
independently.

- **Repository URL:** `https://node-dojo.github.io/no3d-dev/index.json`
- **Blender:** 5.0+
- **License:** GPL-3.0-or-later
- **Umbrella name in Blender:** *No3d Dev*

## Subscribe (recommended)

In Blender 5.0+:

1. Open **Edit → Preferences → Get Extensions → Repositories → +** (new remote).
2. Paste `https://node-dojo.github.io/no3d-dev/index.json`.
3. Refresh. Every extension in this repo appears in **Get Extensions**.
4. Install the ones you want; each has its own preferences page and updates
   on its own cadence.

## Extensions in this repo

### No3d Asset Developer

Turns marked assets into clean, individually-packaged `.blend` files with
metadata, thumbnails, and dev notes — for maintaining a distributable asset
library. Currently also bundles **Save & Reload** (one-click iteration save +
relaunch) and **Claude Pair** (pairs a Blender instance with a Claude Code
terminal via the official Blender MCP add-on) as subpackages; those will
unmerge into their own top-level extensions in a later phase.

Location once installed: **Asset Browser → Context Menu** and
**3D Viewport → N-Panel → No3D Dev**.

Source: `extensions/no3d_asset_developer/`.

## Development

Each extension is a self-contained subdirectory under `extensions/`. Repo-wide
tooling lives at the outer root:

- `tools/check_register.sh` — headless register/unregister gate; iterates
  every extension. Must print `REGISTER_OK` after any registration-touching
  change.
- `tools/build_all.sh` — headless `extension build` per extension into `dist/`.
- `tools/publish_repo.sh` — builds all extensions, aggregates zips, generates
  the static repo `index.json`, force-pushes to gh-pages.

For contributor / AI-agent onboarding, read `AGENTS.md` at the repo root
before touching code. It carries the non-negotiables, Blender quirks, and
the cross-extension conventions (classname prefixes, `bpy.ops`-only for
cross-extension calls, no Python imports across extensions).

## License

Copyright (C) 2026 The Well Tarot, LLC. Every extension in this repo is
released under the GNU General Public License v3.0 or later. See
[LICENSE](./LICENSE).
