# Changelog

## 1.0.39 - First packaged CurveMotion release (2026-10-13)

This release keeps the existing addon version and includes the locally
developed Blender 5.1 marker fixes, performance fixes and compatibility
rebuild below. It is the first tagged CurveMotion release in this repository.

### Marker fixes for Blender 5.1

- Timeline markers are `TimelineMarker` in Blender 5.0+ and no longer support
  ID properties, so reading the `side` custom property crashed every smoothing
  tool with `TypeError: this type doesn't support IDProperties` whenever the
  scene had at least one marker.
- Reference markers are now identified by their name (`L` / `R`, as created by
  the addon) instead of a custom property.
- Creating markers no longer crashes after creation when the custom property
  cannot be stored (older Blender versions still store it).
- If a reference marker is missing, the reference frames stored on the tool
  are used instead of silently returning frame 0.

### Performance fixes

- Anim Offset now runs only while a transform operator is active, instead of
  scanning every selected object and FCurve on every depsgraph update.
- Fast Offset skips repeated updates from the same transform operator.
- Mask blend curves are resolved once per FCurve, zero deltas skip work, and
  sort/handle recalculation only happens when keys actually changed.
- Replaced the per-frame 3D viewport text overlay and temporary theme color
  changes with the workspace status bar, so enabling the addon no longer
  changes user preferences or adds a permanent draw handler.
- Leaving an Anim Offset mask now clears the mask, disables the preview range,
  and restores the full animation range.

### CurveMotion (Blender 5.1 rebuild)

CurveMotion is a renamed, Blender 5.1 rebuild of AnimAide `v1_0_39` from
aresdevo/animaide.

#### Rebrand

- Renamed the project and addon from AnimAide to CurveMotion.
- The addon package, scene property, menus, panels, and operators use the
  new `curvemotion` namespace.

#### Compatibility

- Support Blender 5.1's `ActionChannelbag` for fcurves and groups.
- Add `utils.action_fcurves()` / `utils.action_groups()` helpers so the addon
  keeps working when `mmd_tools` injects legacy `Action.fcurves` / `groups`.
- Use the `group_name` keyword when creating fcurves on Blender 4.3+.
- Remove the `TIME_MT_editor_menus` registration that no longer exists.
- Replace the removed Graph Editor `preview_range` theme color with a fixed
  highlight and fix the header color reset for NLA/Graph/Dope Sheet.

#### Bug fixes

- Key deletion by type no longer crashes when an fcurve has no group.
- Anim Offset no longer crashes when the active object has no animation data.
- Smoothing a selected bone's curves no longer fails on Blender 5.1 with
  `'Bone' object has no attribute 'select'`; the selection check now uses the
  pose bone instead of the edit bone.
