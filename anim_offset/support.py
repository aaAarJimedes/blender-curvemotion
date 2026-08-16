# licence
'''
Copyright (C) 2018 Ares Deveaux


Created by Ares Deveaux

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import os

# from utils.key import global_values
from .. import utils, prefe

# Anim_transform global variables

user_preview_range = {}
user_scene_range = {}
global_values = {}
last_op = None

TRANSFORM_OPERATOR_IDS = {
    'TRANSFORM_OT_translate',
    'TRANSFORM_OT_rotate',
    'TRANSFORM_OT_resize',
    'TRANSFORM_OT_skin_resize',
    'TRANSFORM_OT_transform',
    'TRANSFORM_OT_shear',
    'TRANSFORM_OT_bend',
    'TRANSFORM_OT_tosphere',
    'TRANSFORM_OT_mirror',
    'TRANSFORM_OT_edge_slide',
    'TRANSFORM_OT_vertex_slide',
}

# ---------- Main Tool ------------


def magnet_handlers(scene):
    """Function to be run by the anim_offset Handler"""

    global last_op

    context = bpy.context

    external_op = context.active_operator
    external_op_name = getattr(external_op, 'bl_idname', None)

    if context.scene.tool_settings.use_keyframe_insert_auto or \
            (context.mode != "OBJECT" and context.mode != "POSE"):

        anim_offset = scene.curvemotion.anim_offset
        if anim_offset.mask_in_use:
            close_mask(context)

        bpy.app.handlers.depsgraph_update_post.remove(magnet_handlers)
        utils.remove_message()
        return

    if external_op_name is None or external_op_name not in TRANSFORM_OPERATOR_IDS:
        last_op = None
        return

    curvemotion = context.scene.curvemotion
    anim_offset = curvemotion.anim_offset

    preferences = context.preferences
    pref = preferences.addons[prefe.addon_name].preferences

    if context.scene.curvemotion.anim_offset.mask_in_use:
        cur_frame = context.scene.frame_current
        if cur_frame < scene.frame_start or cur_frame > scene.frame_end:
            if anim_offset.insert_outside_keys:
                add_keys(context)
            return

    # Doesn't refresh repeatedly while the same transform operator is active.
    if pref.ao_fast_offset and external_op_name == last_op:
        return
    last_op = external_op_name

    # context.scene.tool_settings.use_keyframe_insert_auto = False

    selected_objects = context.selected_objects

    for obj in selected_objects:
        action = getattr(obj.animation_data, 'action', None)

        for fcurve in utils.action_fcurves(action) or []:
            if fcurve.data_path.endswith("rotation_mode"):
                continue   #added exception
            magnet(context, obj, fcurve)

    return


def magnet(context, obj, fcurve):
    """Modify all the keys in every fcurve of the current object proportionally to the change in transformation
    on the current frame by the user """

    scene = context.scene

    if fcurve.lock:
        return

    if getattr(fcurve.group, 'name', None) == 'curvemotion':
        return  # we don't want to select keys on reference fcurves

    mask_in_use = scene.curvemotion.anim_offset.mask_in_use
    blend_curve = None
    if mask_in_use:
        blends_action = bpy.data.actions.get('curvemotion')
        blends_curves = utils.action_fcurves(blends_action)
        if blends_curves is not None and len(blends_curves) > 0:
            blend_curve = blends_curves[0]

    delta_y = get_delta(context, obj, fcurve)
    if delta_y == 0:
        return

    changed = False
    for k in fcurve.keyframe_points:

        if not mask_in_use:
            factor = 1
        elif scene.frame_start <= k.co.x <= scene.frame_end:
            factor = 1
        elif blend_curve is not None:
            factor = blend_curve.evaluate(k.co.x)
        else:
            factor = 0

        offset = delta_y * factor
        if offset:
            k.co_ui.y += offset
            changed = True

    if changed:
        fcurve.keyframe_points.sort()
        fcurve.keyframe_points.handles_recalc()

    return


def get_delta(context, obj, fcurve):
    """Determine the transformation change by the user of the current object"""

    cur_frame = bpy.context.scene.frame_current
    anim_data = getattr(obj, 'animation_data', None)
    nla_frame = cur_frame
    if anim_data is not None and hasattr(anim_data, 'nla_tweak_strip_time_to_scene'):
        try:
            nla_frame = int(anim_data.nla_tweak_strip_time_to_scene(cur_frame))
        except Exception:
            nla_frame = cur_frame
    nla_dif = nla_frame - cur_frame
    curve_value = fcurve.evaluate(cur_frame-nla_dif)

    try:
        prop = obj.path_resolve(fcurve.data_path)
    except:
        prop = None

    if prop:
        try:
            target = prop[fcurve.array_index]
        except TypeError:
            target = prop
        try:
            return target - curve_value
        except TypeError:
            return 0
    else:
        return 0


# ----------- Mask -----------


def add_blends():
    """Add a curve with 4 control pints to an action called 'curvemotion' that would act as a mask for anim_offset"""
    action = utils.set_curvemotion_action()
    fcurves = utils.action_fcurves(action)
    if len(fcurves) == 0:
        return utils.curve.new('Magnet', 4)
    else:
        return utils.action_fcurves(action)[0]


def remove_mask(context):
    """Removes the fcurve and action that are been used as a mask for anim_offset"""

    anim_offset = context.scene.curvemotion.anim_offset
    blends_action = bpy.data.actions.get('curvemotion')
    blends_curves = utils.action_fcurves(blends_action)

    anim_offset.mask_in_use = False
    if blends_curves is not None and len(blends_curves) > 0:
        blends_curves.remove(blends_curves[0])
        # reset_timeline_mask(context)

    return


def set_blend_values(context):
    """Modify the position of the fcurve 4 control points that is been used as mask to anim_offset """

    scene = context.scene
    blends_action = bpy.data.actions.get('curvemotion')
    blends_curves = utils.action_fcurves(blends_action)

    if blends_curves is not None:
        blend_curve = blends_curves[0]
        keys = blend_curve.keyframe_points

        left_blend = scene.frame_preview_start
        left_margin = scene.frame_start
        right_margin = scene.frame_end
        right_blend = scene.frame_preview_end

        keys[0].co.x = left_blend
        keys[0].co.y = 0
        keys[1].co.x = left_margin
        keys[1].co.y = 1
        keys[2].co.x = right_margin
        keys[2].co.y = 1
        keys[3].co.x = right_blend
        keys[3].co.y = 0

        mask_interpolation(keys, context)


def mask_interpolation(keys, context):
    anim_offset = context.scene.curvemotion.anim_offset
    interp = anim_offset.interp
    easing = anim_offset.easing

    oposite = None

    if easing == 'EASE_IN':
        oposite = 'EASE_OUT'
    elif easing == 'EASE_OUT':
        oposite = 'EASE_IN'
    elif easing == 'EASE_IN_OUT':
        oposite = 'EASE_IN_OUT'

    keys[0].interpolation = interp
    keys[0].easing = easing
    keys[1].interpolation = 'LINEAR'
    keys[1].easing = 'EASE_IN_OUT'
    keys[2].interpolation = interp
    keys[2].easing = oposite


def add_keys(context):
    selected_objects = context.selected_objects

    for obj in selected_objects:
        action = getattr(obj.animation_data, 'action', None)

        for fcurve in utils.action_fcurves(action) or []:

            if fcurve.lock:
                return

            if getattr(fcurve.group, 'name', None) == 'curvemotion':
                return  # we don't want to select keys on reference fcurves

            keys = fcurve.keyframe_points
            cur_index = utils.key.on_current_frame(fcurve)
            delta_y = get_delta(context, obj, fcurve)

            if not cur_index:
                cur_frame = context.scene.frame_current
                y = fcurve.evaluate(cur_frame) + delta_y
                utils.key.insert_key(keys, cur_frame, y)
            else:
                key = keys[cur_index]
                key.co_ui.y += delta_y


# -------- For mask interface -------


def set_timeline_ranges(context, left_blend, left_margin, right_margin, right_blend):
    """Use the timeline playback and preview ranges to represent the mask"""

    scene = context.scene
    scene.use_preview_range = True

    scene.frame_preview_start = left_blend
    scene.frame_start = left_margin
    scene.frame_end = right_margin
    scene.frame_preview_end = right_blend


def reset_timeline_mask(context):
    """Resets the timeline playback and preview ranges to what the user had it as"""

    scene = context.scene
    anim_offset = scene.curvemotion.anim_offset

    scene.frame_preview_start = anim_offset.user_preview_start
    scene.frame_preview_end = anim_offset.user_preview_end
    scene.use_preview_range = anim_offset.user_preview_use
    scene.frame_start = anim_offset.user_scene_start
    scene.frame_end = anim_offset.user_scene_end
    # scene.tool_settings.use_keyframe_insert_auto = anim_offset.user_scene_auto


def reset_timeline_blends(context):
    """Resets the timeline playback and preview ranges to what the user had it as"""

    scene = context.scene
    anim_offset = scene.curvemotion.anim_offset

    scene.frame_preview_start = anim_offset.user_preview_start
    scene.frame_preview_end = anim_offset.user_preview_end
    scene.use_preview_range = anim_offset.user_preview_use


def store_user_timeline_ranges(context):
    """Stores the timeline playback and preview ranges"""

    scene = context.scene
    anim_offset = scene.curvemotion.anim_offset

    anim_offset.user_preview_start = scene.frame_preview_start
    anim_offset.user_preview_end = scene.frame_preview_end
    anim_offset.user_preview_use = scene.use_preview_range
    anim_offset.user_scene_start = scene.frame_start
    anim_offset.user_scene_end = scene.frame_end
    # anim_offset.user_scene_auto = scene.tool_settings.use_keyframe_insert_auto


def get_full_animation_range(context):
    """Return the start/end frames covering the selected objects' actions."""

    objects = context.selected_objects
    if not objects:
        objects = bpy.data.objects

    ranges = []
    for obj in objects:
        anim_data = getattr(obj, 'animation_data', None)
        if anim_data is None:
            continue
        action = getattr(anim_data, 'action', None)
        if action is None:
            continue

        frame_range = getattr(action, 'frame_range', None)
        if frame_range is not None:
            try:
                ranges.append((int(frame_range[0]), int(frame_range[1])))
                continue
            except Exception:
                pass

        fcurves = utils.action_fcurves(action)
        if fcurves is None:
            continue
        for fcurve in fcurves:
            points = fcurve.keyframe_points
            if points:
                ranges.append((int(points[0].co.x), int(points[-1].co.x)))

    if not ranges:
        return None, None
    return min(start for start, end in ranges), max(end for start, end in ranges)


def close_mask(context):
    """Remove the mask curve, disable the preview range, and restore the full animation range."""

    remove_mask(context)
    reset_timeline_mask(context)

    scene = context.scene
    scene.use_preview_range = False
    start, end = get_full_animation_range(context)
    if start is not None and end is not None:
        scene.frame_start = start
        scene.frame_end = end


# ---------- Functions for Operators ------------


def poll(context):
    """Poll for all the anim_offset related operators"""

    objects = context.selected_objects
    area = context.area.type
    return objects is not None and area == 'GRAPH_EDITOR' or area == 'DOPESHEET_EDITOR' or area == 'VIEW_3D'


def get_anim_offset_globals(context, obj):
    """Get global values for the anim_offset"""

    anim = obj.animation_data
    if anim is None:
        return
    if utils.action_fcurves(anim.action) is None:
        return

    fcurves = utils.action_fcurves(obj.animation_data.action)

    curves = {}

    for fcurve_index, fcurve in fcurves.items():

        if fcurve.lock is True:
            continue

        cur_frame = context.scene.frame_current
        cur_frame_y = fcurve.evaluate(cur_frame)

        values = {'x': cur_frame, 'y': cur_frame_y}

        curves[fcurve_index]['current_frame'] = values

    global_values[obj.name] = curves
