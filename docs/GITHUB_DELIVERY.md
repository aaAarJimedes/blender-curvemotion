# Building and publishing CurveMotion

The primary repository is `aaAarJimedes/blender-curvemotion` (public), with
`main` as its only maintained branch. The original AnimAide author and
GPL-3.0-or-later notices must remain in source and installable packages.

## Build

From the repository root, use Python 3.10+ and Git:

```powershell
python tools/build_release.py --output-dir '<delivery-directory>'
```

The output directory must be outside the source checkout. The script reads
the existing `bl_info` version and writes an installable ZIP containing the
`curvemotion/` package, a build manifest with commit ID and per-file hashes,
and a SHA-256 checksum file. It excludes Git metadata, caches, test code and
development tools. The manifest records uncommitted changes as
`source_dirty: true`; only publish a build with `source_dirty: false`.

## Validate the package

Use a new, disposable profile and a real Blender 5.1 executable. The example
environment variables affect only the current shell and child process:

```powershell
$taskProfile = '<temporary-directory>/blender-profile'
$env:BLENDER_USER_RESOURCES = $taskProfile
$env:BLENDER_USER_CONFIG = "$taskProfile/config"
$env:BLENDER_USER_SCRIPTS = "$taskProfile/scripts"
$env:BLENDER_USER_EXTENSIONS = "$taskProfile/extensions"
$env:BLENDER_USER_DATAFILES = "$taskProfile/datafiles"
blender --background --factory-startup --python-exit-code 1 --python tests/blender_release_smoke.py -- '<package.zip>' $taskProfile
```

Success requires exit code 0 and `CURVEMOTION_RELEASE_SMOKE_PASSED`. This checks
ZIP installation, registration, reference-marker creation/replacement/removal,
missing-marker fallbacks, preservation of unrelated markers, layered action
reference values, a real Graph Editor smooth operation and Anim Offset key
value propagation. It does not certify interactive dragging, all tools, all
scene types, older Blender versions or every other installed addon.

## Publish

- Use the local Git and GitHub CLI with the existing account. Check the
  repository identity, working tree, remote branches, tags and all releases.
- Commit only intended source changes, push `main` normally, build from that
  clean commit and repeat the package check. Create a version tag only after
  the package passes. Never move an existing tag or rewrite history.
- Keep one official release page. Attach the ZIP, build manifest and checksum
  file as real assets. Before replacing a release page, retain all previous
  notes and assets on the retained page and verify every migrated download.
- Download each uploaded asset through GitHub CLI, compare its size and SHA-256
  against the local file, and check the manifest's source commit and ZIP file
  list. An upload response alone is not verification.
- This addon currently has no online updater or `update.json` endpoint.

## Workspace locations

On the maintained Windows workspace:

- Source: `D:\Agent Workspaces\Agent Tools\CurveMotion\curvemotion-5.1-fixed`
- Packages: `D:\Agent Workspaces\Agent Delivery\CurveMotion\releases`
- Temporary build/test profiles: `D:\Agent Workspaces\Agent Temp\CurveMotion`

The original `curvemotion-5.1-fixed.zip` in the delivery directory and the
pre-marker-fix ZIP in the temporary task directory are historical assets.
Do not overwrite them with new builds or delete them as test caches.
