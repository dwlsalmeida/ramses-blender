#  -------------------------------------------------------------------------
#  Copyright (C) 2019 Daniel Werner Lima Souza de Almeida
#                     dwlsalmeida at gmail dot com
#  -------------------------------------------------------------------------
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
#  -------------------------------------------------------------------------

import bpy
import math
import pathlib
from . import debug_utils
from . import intermediary_representation
from . import utils
log = debug_utils.get_debug_logger()


class MaterialBakeConfig():
    def __init__(self,
                 bake_width: int = 1024,
                 bake_height: int = 1024,
                 bake_dir: str = '',
                 bake_type: str = 'COMBINED',
                 auto_unwrap_if_needed: bool = True,
                 enabled: bool = False):
        self.bake_width = bake_width
        self.bake_height = bake_height
        self.bake_dir = bake_dir if bake_dir else utils.get_addon_path()
        self.bake_type = bake_type
        self.auto_unwrap_if_needed = auto_unwrap_if_needed
        self.enabled = enabled

        assert self.bake_type in ('COMBINED', 'AO', 'SHADOW', 'NORMAL',
            'UV', 'ROUGHNESS', 'EMIT', 'ENVIRONMENT', 'DIFFUSE', 'GLOSSY', 'TRANSMISSION',
            'SUBSURFACE'), f'Unknown bake type {self.bake_type}'

        assert pathlib.Path(self.bake_dir).exists(), f'Bake directory does not exist:{self.bake_dir}'

class MaterialBaker():
    """Controls baking for a given (mesh) node.

    Cycles shaders and lighting can be baked to image textures. This has a few different purposes, most commonly:

    Baking textures like base color or normal maps for export to game engines.
    Baking ambient occlusion or procedural textures, as a base for texture painting or further edits.
    Creating light maps to provide global illumination or speed up rendering in games.

    See https://docs.blender.org/manual/en/latest/render/cycles/baking.html for further info"""

    def __init__(self, bake_config: MaterialBakeConfig = None):
        self.current_node = None # Points to a MeshNode
        self.current_layer = None # The layer for the current node

        if bake_config:
            assert isinstance(bake_config, MaterialBakeConfig)
            self.config = bake_config
        else:
            self.config = MaterialBakeConfig()

        if self.config.bake_type != 'COMBINED':
            raise NotImplementedError('This exporter only supports Bake COMBINED for now')

    def set_current_node(self, node, bake_config: MaterialBakeConfig = None):
        assert node
        self.current_node = node
        self.current_layer = node.find_view_layer()
        assert self.current_layer

        if bake_config:
            self.config = bake_config

        assert pathlib.Path(self.config.bake_dir).exists(), f'Bake directory does not exist:{self.config.bake_dir}'

    def clear_current_node(self):
        self.current_node = None
        self.current_layer = None
        self.config.bake_dir = ''

    def do_node(self, node=None, bake_config: MaterialBakeConfig = None):
        if node:
            self.set_current_node(node, bake_config)

        assert self.current_node
        assert isinstance(self.current_node, intermediary_representation.MeshNode), 'Only meshes are supported for now'

        if self.config.auto_unwrap_if_needed:
            self._smart_project_if_needed()

        assert self.current_node.is_UV_unwrapped(), "Node should be unwrapped by now"

        textures = self.bake_to_disk()

        self.current_node.textures = textures # RAMSES can load directly from PNG

    def _smart_project_if_needed(self):
        assert isinstance(self.current_node, intermediary_representation.MeshNode), 'Only meshes are supported for now'

        if not self.current_node.is_UV_unwrapped():

            with utils.this_object_selected(self.current_node.blender_object, make_active=True, view_layer=self.current_layer.view_layer):
                log.debug(f'Smart UV unwrapping node "{str(self.current_node)}"')

                for face in self.current_node.get_faces():
                    face.select_set(True)

                uv = self.current_node.create_UV_layer()
                uv.active = True

                old_mode = None
                if bpy.context.object.mode != 'EDIT':
                    old_mode = bpy.context.object.mode
                    bpy.ops.object.mode_set(mode='EDIT')

                bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin = 0.02)

                if old_mode:
                    bpy.ops.object.mode_set(mode=old_mode)

    def bake_to_disk(self):
        ret = {}

        with utils.this_object_selected(self.current_node.blender_object, make_active=True, view_layer=self.current_layer.view_layer):

            assert self.current_node.is_UV_unwrapped(), "Node should be unwrapped by now"
            assert self.config.bake_type in ('COMBINED', 'AO', 'SHADOW', 'NORMAL',
             'UV', 'ROUGHNESS', 'EMIT', 'ENVIRONMENT', 'DIFFUSE', 'GLOSSY', 'TRANSMISSION',
             'SUBSURFACE'), f'Unknown bake type {self.config.bake_type}'

            images = self.current_node.create_IMG_nodes_for_baking(width=self.config.bake_width, height=self.config.bake_height)

            for image in images:
                filepath = str(pathlib.Path(self.config.bake_dir)/image.name/f'{self.config.bake_type}.png')
                image.filepath = filepath
                bpy.ops.object.bake(type=self.config.bake_type,
                                    filepath=filepath,
                                    width=self.config.bake_width,
                                    height=self.config.bake_height,
                                    save_mode='EXTERNAL',
                                    use_split_materials=False,
                                    use_automatic_name=False,
                                    use_clear=True)

                image.save_render(filepath)

                assert pathlib.Path(filepath).exists(), "Baking operation did not produce a valid image file!"

                bake_name = f'bake_{self.config.bake_type.lower()}'
                ret[bake_name] = filepath
                log.debug(f'Saved baked texture to disk for node "{str(self.current_node)}". Filename is {filepath}')

            return ret
