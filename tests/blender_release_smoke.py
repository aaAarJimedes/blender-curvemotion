"""Run with Blender --background --factory-startup --python-exit-code 1.

Pass -- PACKAGE.zip ISOLATED_PROFILE after this script. Set Blender user
resource/config/script directories to that profile before starting Blender.
"""

import json
import os
import sys
from pathlib import Path

import bpy


package, profile = [Path(value).resolve() for value in sys.argv[sys.argv.index("--") + 1:]]
for variable in ("BLENDER_USER_RESOURCES", "BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS"):
    value = Path(os.environ[variable]).resolve()
    assert value == profile or profile in value.parents, (variable, value)
scripts = Path(bpy.utils.user_resource("SCRIPTS", create=True)).resolve()
assert scripts == profile or profile in scripts.parents, scripts

assert bpy.ops.preferences.addon_install(filepath=str(package), overwrite=True) == {"FINISHED"}
assert bpy.ops.preferences.addon_enable(module="curvemotion") == {"FINISHED"}
import curvemotion
from curvemotion import utils
from curvemotion.curve_tools import support
from curvemotion.anim_offset import support as offset_support

assert profile in Path(curvemotion.__file__).resolve().parents
addon = bpy.context.preferences.addons["curvemotion"]
pref = addon.preferences
scene = bpy.context.scene
tool = scene.curvemotion.tool
markers = scene.timeline_markers
markers.new("Unrelated", frame=33)
markers.new("diagnostic", frame=55)
assert support.set_ref_marker(bpy.context) == (tool.left_ref_frame, tool.right_ref_frame)

tool.left_ref_frame, tool.right_ref_frame = 100, 200
utils.add_marker(name="", side="L", frame=100)
utils.add_marker(name="", side="R", frame=200)
assert support.set_ref_marker(bpy.context) == (100, 200)
utils.add_marker(name="", side="L", frame=150)
assert support.set_ref_marker(bpy.context) == (150, 200)
utils.remove_marker("L")
assert support.set_ref_marker(bpy.context) == (100, 200)
scene.frame_current = 77
assert bpy.ops.anim.aide_get_ref_frame(side="L") == {"FINISHED"}
assert support.set_ref_marker(bpy.context) == (77, 200)
pref.ct_use_markers = False
assert set(marker.name for marker in markers) == {"Unrelated", "diagnostic"}
assert support.set_ref_marker(bpy.context) == (77, 200)
pref.ct_use_markers = True
assert support.set_ref_marker(bpy.context) == (77, 200)

# Test the real Graph Editor operator, including get_globals and its marker
# lookup, against a real layered ActionChannelbag and an animated object.
bpy.ops.object.select_all(action="DESELECT")
obj = bpy.data.objects.new("CurveMotionSmoke", None)
scene.collection.objects.link(obj)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
for frame, value in ((1, 0.0), (10, 9.0), (20, 0.0)):
    obj.location.x = value
    obj.keyframe_insert(data_path="location", index=0, frame=frame)
fcurve = utils.action_fcurves(obj.animation_data.action)[0]
for key in fcurve.keyframe_points:
    key.select_control_point = True
    key.select_left_handle = False
    key.select_right_handle = False
utils.add_marker(name="", side="L", frame=1)
utils.add_marker(name="", side="R", frame=20)
area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
area.type = "GRAPH_EDITOR"
region = next(region for region in area.regions if region.type == "WINDOW")
with bpy.context.temp_override(area=area, region=region):
    support.get_globals(bpy.context)
    curves = support.global_values["objects"][obj.name]["actions"]["transform_action"]["curves"]
    assert curves, "get_globals returned no animation curves"
    for curve in curves.values():
        assert curve["ref_frames"]["left_y"] == fcurve.evaluate(1)
        assert curve["ref_frames"]["right_y"] == fcurve.evaluate(20)
    result = bpy.ops.anim.aide_smooth("EXEC_DEFAULT", op_context="EXEC_DEFAULT", factor=1.0)
    assert result == {"FINISHED"}, result
assert abs(fcurve.keyframe_points[0].co.y) < 1e-6
assert abs(fcurve.keyframe_points[1].co.y - 4.0) < 1e-6
assert abs(fcurve.keyframe_points[2].co.y) < 1e-6

# Anim Offset should apply a real transform delta to all keys without a mask.
scene.frame_set(1)
before = [key.co.y for key in fcurve.keyframe_points]
obj.location.x += 3.0
offset_support.magnet(bpy.context, obj, fcurve)
assert all(abs(key.co.y - value - 3.0) < 1e-6
           for key, value in zip(fcurve.keyframe_points, before))

# Disabling and enabling again catches registration/unregistration leaks.
assert bpy.ops.preferences.addon_disable(module="curvemotion") == {"FINISHED"}
assert not hasattr(bpy.types.Scene, "curvemotion")
assert bpy.ops.preferences.addon_enable(module="curvemotion") == {"FINISHED"}
assert bpy.ops.preferences.addon_disable(module="curvemotion") == {"FINISHED"}
print("CURVEMOTION_RELEASE_SMOKE_PASSED " + json.dumps({
    "blender": bpy.app.version_string,
    "version": list(curvemotion.bl_info["version"]),
    "checks": ["zip_install", "enable_disable_enable", "reference_marker_lifecycle",
               "unrelated_marker_preservation", "missing_marker_fallback",
               "layered_action_reference_values", "graph_editor_smooth_values", "anim_offset_delta"],
}))
