#  -------------------------------------------------------------------------
#  Copyright (C) 2019 Daniel Werner Lima Souza de Almeida
#                     dwlsalmeida at gmail dot com
#  -------------------------------------------------------------------------
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
#  -------------------------------------------------------------------------

import pathlib
import os


class ExportableScene():
    """A RAMSES Scene ready to be visualized / saved"""
    def __init__(self,
                 ramses,
                 ramses_scene,
                 blender_scene_representation):
        self.ramses = ramses
        self._ramses_scene = ramses_scene
        self._blender_scene_representation = blender_scene_representation

        # Paths are set at a later stage
        self.output_path = None

    @property
    def ramses_scene(self):
        return self._ramses_scene

    @property
    def blender_scene(self):
        return self._blender_scene_representation.scene

    @property
    def scene_representation(self):
        return self._blender_scene_representation

    def save(self):
        """Persists the RAMSES scene."""

        ramses_scene_file = os.path.join(self.output_path, f'{self.blender_scene.name}.ramses')
        ramses_scene_resources_file = os.path.join(self.output_path, f'{self.blender_scene.name}.ramres')
        self.ramses_scene.saveToFiles(str(ramses_scene_file),
                                      str(ramses_scene_resources_file),
                                      True)

    def get_validation_report(self):
        """Returns the validation report issued by RAMSES."""
        return str(self.ramses_scene.getValidationReport())

    def is_valid(self):
        """Whether the underlying RAMSES scene is valid."""
        report = self.get_validation_report()
        # TODO: FIXME. A RenderGroup containing only nested RenderGroups triggers a warning.
        #              This is the default for Blender, however, since the default scene is
        #              organized as follows: 'Scene collection' -> 'Collection' -> (cube, camera, light).
        #              Therefore, the topmost RAMSES RenderGroup has a nested RenderGroup and no meshes.
        #              Maybe this should be reconsidered in RAMSES, as it produces completely
        #              valid output.
        empty_render_group = 'WARNING: rendergroup does not contain any meshes'
        return len(report) == 0 or empty_render_group in report

    def set_output_dir(self, output_dir: str):
        """Sets the output directory if this scene is to be saved"""

        if not pathlib.Path(output_dir).is_dir():
            raise RuntimeError('Invalid output directory specified.')

        self.output_path = output_dir

    def to_text(self) -> str:
        """Returns the RAMSES text representation for the underlying
        RAMSES scene"""
        text_representation = self.ramses_scene.toText()
        assert text_representation
        return text_representation
