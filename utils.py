#  -------------------------------------------------------------------------
#  Copyright (C) 2019 Daniel Werner Lima Souza de Almeida
#                     dwlsalmeida at gmail dot com
#  -------------------------------------------------------------------------
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
#  -------------------------------------------------------------------------

import os
import bpy
from contextlib import contextmanager
from . import debug_utils
from . import baking
log = debug_utils.get_debug_logger()

def get_addon_path():
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    return directory

@contextmanager
def this_object_selected(a_object, make_active:bool=False, view_layer=None):
    """A helper for selecting only this object for operations and then
    restoring the selection state"""
    selection_status = {}
    # https://docs.blender.org/api/blender2.8/bpy.types.Depsgraph.html
    # Selection depends on a context and is only valid for original objects. This means we need
    # to request the original object from the known evaluated one.
    a_object = a_object.original
    for object_ in bpy.data.objects:
        selection_status[object_.name_full] = object_.select_get()

    bpy.ops.object.select_all(action='DESELECT')
    a_object.select_set(True)

    if make_active and view_layer:
        view_layer.objects.active = a_object
        selection_status['previously_active_view_layer'] = bpy.context.window.view_layer
        bpy.context.window.view_layer = view_layer

    yield a_object

    for object_ in bpy.data.objects:
        was_selected = selection_status[object_.name_full]
        object_.select_set(was_selected)

        if make_active and view_layer:
            view_layer.objects.active = None
            bpy.context.window.view_layer = selection_status['previously_active_view_layer']


class CustomParameters():
    """Extra parameters we might set that are not a part of the Blender scene itself"""
    def __init__(self):
        self.shader_dir = ''
        self.render_technique = ''
        self.material_bake = baking.MaterialBakeConfig()
