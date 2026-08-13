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
from . import support
from bpy.types import Panel, Menu


class CURVEMOTION_PT:
    bl_label = "Anim Offset"
    bl_region_type = 'UI'
    bl_category = 'CurveMotion'

    def draw(self, context):

        anim_offset = context.scene.curvemotion.anim_offset
        mask_in_use = context.scene.curvemotion.anim_offset.mask_in_use

        layout = self.layout

        # layout.label(text='Now Anim Offset buttons')
        # layout.label(text='are in the timeline')
        # layout.label(text='header next to CurveMotion')
        # layout.label(text='menu')

        if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
            layout.operator("anim.aide_deactivate_anim_offset", text='Deactivate', depress=True, icon='TEMP')
        else:
            layout.operator("anim.aide_activate_anim_offset", text='Activate', icon='TEMP')

        row = layout.row(align=True)

        if context.area.type != 'VIEW_3D' or context.area.type != 'NLA_EDITOR':

            if mask_in_use:
                row.operator("anim.aide_delete_anim_offset_mask", text='Deactivate Mask', depress=True, icon='SELECT_SUBTRACT')
                sub = row.row(align=True)
                sub.active = True
                op = sub.operator("anim.aide_add_anim_offset_mask", text='', icon='GREASEPENCIL')
                op.sticky = True

            else:
                op = row.operator("anim.aide_add_anim_offset_mask", text='Mask', icon='SELECT_SUBTRACT')
                op.sticky = False
                sub = row.row(align=True)
                sub.active = False

            sub.operator('anim.aide_anim_offset_settings', text='', icon='PREFERENCES', emboss=True)

        # row = layout.row(align=False)
        # row.active = status
        # sub.operator('anim.aide_anim_offset_settings', text='', icon='PREFERENCES', emboss=True)
        # sub.popover(panel="CURVEMOTION_PT_preferences", text="")

        # if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
        #     row.operator("anim.aide_deactivate_anim_offset", text='Deactivate', depress=True, icon='OVERLAY')
        # else:
        #     row.operator("anim.aide_activate_anim_offset", text='Activate', icon='OVERLAY')

        # row.operator('anim.aide_anim_offset_settings', text='', icon='PREFERENCES', emboss=True)
        #
        # row = layout.row(align=True)
        #
        # if context.area.type != 'VIEW_3D':
        #     mask_in_use = context.scene.curvemotion.anim_offset.mask_in_use
        #     if mask_in_use:
        #         name = 'Modify Mask'
        #         depress = True
        #
        #     else:
        #         name = 'Mask'
        #         depress = False
        #
        #     row.operator("anim.aide_add_anim_offset_mask", text=name, depress=depress, icon='SELECT_SUBTRACT')
        #     row.operator("anim.aide_delete_anim_offset_mask", text='', icon='TRASH')
        # if mask_in_use:
        #     layout.label(text='Mask blend interpolation:')
        #     row = layout.row(align=True)
        #     row.prop(anim_offset, 'easing', text='', icon_only=False)
        #     row.prop(anim_offset, 'interp', text='', expand=True)


class CURVEMOTION_PT_anim_offset_3d(Panel, CURVEMOTION_PT):
    bl_idname = 'CURVEMOTION_PT_anim_offset_3d'
    bl_space_type = 'VIEW_3D'


class CURVEMOTION_PT_anim_offset_ge(Panel, CURVEMOTION_PT):
    bl_idname = 'CURVEMOTION_PT_anim_offset_ge'
    bl_space_type = 'GRAPH_EDITOR'


class CURVEMOTION_PT_anim_offset_de(Panel, CURVEMOTION_PT):
    bl_idname = 'CURVEMOTION_PT_anim_offset_de'
    bl_space_type = 'DOPESHEET_EDITOR'


class CURVEMOTION_MT_anim_offset(Menu):
    bl_idname = 'CURVEMOTION_MT_anim_offset'
    bl_label = "Anim Offset"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        layout.operator('anim.aide_activate_anim_offset', text='On')
        layout.operator('anim.aide_deactivate_anim_offset', text='Off')


class CURVEMOTION_MT_anim_offset_mask(Menu):
    bl_idname = 'CURVEMOTION_MT_anim_offset_mask'
    bl_label = "Anim Offset Mask"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        if context.area.type != 'VIEW_3D':
            layout.operator('anim.aide_add_anim_offset_mask', text='Add/Modify')
            layout.operator('anim.aide_delete_anim_offset_mask', text='Delete')


class CURVEMOTION_MT_pie_anim_offset(Menu):
    bl_idname = "CURVEMOTION_MT_pie_anim_offset"
    bl_label = "AnimOffset"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator('anim.aide_activate_anim_offset', text='AnimOffset Without Mask')
        pie.operator('anim.aide_add_anim_offset_mask', text='Add AnimOffset Mask')
        pie.operator('anim.aide_delete_anim_offset_mask', text='Delete AnimOffset Mask')
        pie.operator('anim.aide_deactivate_anim_offset', text='Deactivate AnimOffset')


class CURVEMOTION_PT_preferences(Panel):
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'HEADER'
    bl_label = "Anim Offset Settings"
    bl_options = {'HIDE_HEADER'}

    # @classmethod
    # def poll(cls, context):
    #     return support.magnet_handlers in bpy.app.handlers.depsgraph_update_post

    def draw(self, context):
        anim_offset = context.scene.curvemotion.anim_offset

        layout = self.layout

        # if support.magnet_handlers not in bpy.app.handlers.depsgraph_update_post:
        #     layout.active = False

        mask_in_use = context.scene.curvemotion.anim_offset.mask_in_use
        if not mask_in_use:
            layout.active = False

        # layout.label(text='Settings')
        # layout.separator()
        # layout.prop(anim_offset, 'end_on_release', text='masking ends on mouse release')
        # layout.prop(anim_offset, 'fast_mask', text='Fast offset calculation')
        # if context.area.type != 'VIEW_3D':

        layout.prop(anim_offset, 'insert_outside_keys', text='Auto Key outside margins')
        layout.separator()
        layout.label(text='Mask blend interpolation:')
        row = layout.row(align=True)
        if not mask_in_use:
            row.active = False
        row.prop(anim_offset, 'easing', text='', icon_only=False)
        row.prop(anim_offset, 'interp', text='', expand=True)


def draw_anim_offset(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.separator()

    if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
        row.operator("anim.aide_deactivate_anim_offset", text='', depress=True, icon='TEMP')
    else:
        row.operator("anim.aide_activate_anim_offset", text='', icon='TEMP')


def draw_anim_offset_mask(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.separator()

    if support.magnet_handlers in bpy.app.handlers.depsgraph_update_post:
        row.operator("anim.aide_deactivate_anim_offset", text='', depress=True, icon='TEMP')
    else:
        row.operator("anim.aide_activate_anim_offset", text='', icon='TEMP')

    mask_in_use = context.scene.curvemotion.anim_offset.mask_in_use
    if mask_in_use:
        row.operator("anim.aide_delete_anim_offset_mask", text='', depress=True, icon='SELECT_SUBTRACT')
        op = row.operator("anim.aide_add_anim_offset_mask", text='', icon='GREASEPENCIL')
        op.sticky = True
        sub = row.row(align=True)
        sub.active = True
    else:
        op = row.operator("anim.aide_add_anim_offset_mask", text='', icon='SELECT_SUBTRACT')
        op.sticky = False
        sub = row.row(align=True)
        sub.active = False

    sub.popover(panel="CURVEMOTION_PT_preferences", text="")


menu_classes = (
    CURVEMOTION_MT_anim_offset,
    CURVEMOTION_MT_anim_offset_mask,
    CURVEMOTION_MT_pie_anim_offset,
    CURVEMOTION_PT_preferences,
)

panel_classes = (
    CURVEMOTION_PT_anim_offset_3d,
    CURVEMOTION_PT_anim_offset_ge,
    CURVEMOTION_PT_anim_offset_de,
)
