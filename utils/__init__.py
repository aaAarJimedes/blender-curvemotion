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

from .general import *
from . import curve, key


def get_action_channelbag(action):
    """Return the action channelbag that holds fcurves/groups in Blender 4.3+."""

    if action is None:
        return None

    # Blender < 4.3: fcurves and groups live directly on the action.
    # mmd_tools can also inject a compatibility fcurves/groups property on
    # newer actions, so use the layers/slots structure as the real signal.
    if not hasattr(action, 'layers') or not hasattr(action, 'slots'):
        return None

    from bpy_extras import anim_utils

    # Prefer a bag that already holds fcurves.
    if hasattr(action, 'layers'):
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag is not None and len(bag.fcurves):
                        return bag

    # Fall back to the slot assigned to the datablock, then the first slot.
    slot = None
    if hasattr(action, 'slots'):
        if action.slots:
            slot = action.slots[0]

    if slot is None:
        if not hasattr(action, 'slots'):
            return None
        # Standalone helper action (e.g. 'curvemotion') has no target datablock.
        slot = action.slots.new('OBJECT', 'Slot')

    try:
        return anim_utils.action_ensure_channelbag_for_slot(action, slot)
    except Exception:
        # No layer/strip support on this build; keep the old behavior.
        return None


def action_fcurves(action):
    """Return an fcurves collection compatible with action.fcurves."""

    if action is None:
        return None
    if not hasattr(action, 'layers') or not hasattr(action, 'slots'):
        if hasattr(action, 'fcurves'):
            return action.fcurves
        return None
    bag = get_action_channelbag(action)
    if bag is None:
        return None
    return bag.fcurves


def action_groups(action):
    """Return an action groups collection compatible with action.groups."""

    if action is None:
        return None
    if not hasattr(action, 'layers') or not hasattr(action, 'slots'):
        if hasattr(action, 'groups'):
            return action.groups
        return None
    bag = get_action_channelbag(action)
    if bag is None:
        return None
    return bag.groups


def action_fcurves_for_animdata(anim_data):
    """Return fcurves for an animation_data assignment."""

    if anim_data is None:
        return None
    return action_fcurves(getattr(anim_data, 'action', None))


def find_channelbag(obj):
    """Find the channelbag that owns an fcurve or fcurves collection."""

    if obj is None:
        return None

    action = getattr(obj, 'id_data', None)
    if action is None:
        return None

    if not hasattr(action, 'layers'):
        return None
    if not hasattr(action, 'slots'):
        return None

    fcurves = getattr(obj, 'fcurves', None)
    fcurve = None if fcurves is not None else obj
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag is None:
                    continue
                if fcurves is not None:
                    if fcurves == bag.fcurves:
                        return bag
                elif fcurve is not None:
                    for candidate in bag.fcurves:
                        if candidate == fcurve:
                            return bag
    return None
