# Changelog

## Unreleased - Performance fixes

- Anim Offset now runs only while a transform operator is active, instead of
  scanning every selected object and FCurve on every depsgraph update.
- Fast Offset skips repeated updates from the same transform operator.
- Mask blend curves are resolved once per FCurve, zero deltas skip work, and
  sort/handle recalculation only happens when keys actually changed.
- Replaced the per-frame 3D viewport text overlay and temporary theme color
  changes with the workspace status bar, so enabling the addon no longer
  changes user preferences or adds a permanent draw handler.

## 1.0.39 - CurveMotion (Blender 5.1 rebuild)

CurveMotion is a renamed, Blender 5.1 rebuild of AnimAide `v1_0_39` from
aresdevo/animaide.

### Rebrand

- Renamed the project and addon from AnimAide to CurveMotion.
- The addon package, scene property, menus, panels, and operators use the
  new `curvemotion` namespace.

### Compatibility

- Support Blender 5.1's `ActionChannelbag` for fcurves and groups.
- Add `utils.action_fcurves()` / `utils.action_groups()` helpers so the addon
  keeps working when `mmd_tools` injects legacy `Action.fcurves` / `groups`.
- Use the `group_name` keyword when creating fcurves on Blender 4.3+.
- Remove the `TIME_MT_editor_menus` registration that no longer exists.
- Replace the removed Graph Editor `preview_range` theme color with a fixed
  highlight and fix the header color reset for NLA/Graph/Dope Sheet.

### Bug fixes

- Key deletion by type no longer crashes when an fcurve has no group.
- Anim Offset no longer crashes when the active object has no animation data.
- Smoothing a selected bone's curves no longer fails on Blender 5.1 with
  `'Bone' object has no attribute 'select'`; the selection check now uses the
  pose bone instead of the edit bone.
