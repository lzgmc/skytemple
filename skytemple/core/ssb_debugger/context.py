#  Copyright 2020 Parakoopa
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from typing import TYPE_CHECKING, Optional, List

from explorerscript.source_map import SourceMapPositionMark
from skytemple.core.rom_project import RomProject
from skytemple.core.ssb_debugger.ssb_loaded_file_handler import SsbLoadedFileHandler
from skytemple_files.common.ppmdu_config.data import Pmd2Data
from skytemple_files.common.project_file_manager import ProjectFileManager
from skytemple_files.common.script_util import ScriptFiles, load_script_files, SCRIPT_DIR
from skytemple_ssb_debugger.context.abstract import AbstractDebuggerControlContext

if TYPE_CHECKING:
    from skytemple_ssb_debugger.model.ssb_files.file_manager import SsbFileManager
    from skytemple.core.ssb_debugger.manager import DebuggerManager
    from skytemple_ssb_debugger.model.ssb_files.file import SsbLoadedFile


class SkyTempleMainDebuggerControlContext(AbstractDebuggerControlContext):
    def __init__(self, manager: 'DebuggerManager'):
        self._manager = manager

    def allows_interactive_file_management(self) -> bool:
        return False

    def before_quit(self) -> bool:
        return True

    def on_quit(self):
        self._manager.on_close()

    def open_rom(self, filename: str):
        return NotImplementedError()

    def get_project_dir(self) -> str:
        return self._project_fm.dir()

    def load_script_files(self) -> ScriptFiles:
        return load_script_files(RomProject.get_current().get_rom_folder(SCRIPT_DIR))

    def is_project_loaded(self) -> bool:
        return RomProject.get_current() is not None

    def get_rom_filename(self) -> str:
        return RomProject.get_current().filename

    def save_rom(self):
        # We only save the current ROM contents!
        RomProject.get_current().save_as_is()

    def get_static_data(self) -> Pmd2Data:
        return RomProject.get_current().get_rom_module().get_static_data()

    def get_project_filemanager(self) -> ProjectFileManager:
        return self._project_fm

    def get_ssb(self, filename, ssb_file_manager: 'SsbFileManager') -> 'SsbLoadedFile':
        return RomProject.get_current().open_file_in_rom(filename, SsbLoadedFileHandler,
                                                         filename=filename,
                                                         static_data=self.get_static_data(),
                                                         ssb_file_manager=ssb_file_manager,
                                                         project_fm=self._project_fm)

    def save_ssb(self, filename, ssb_model, ssb_file_manager: 'SsbFileManager'):
        project = RomProject.get_current()
        ssb_loaded_file = self.get_ssb(filename, ssb_file_manager)
        ssb_loaded_file.ssb_model = ssb_model
        project.prepare_save_model(filename, assert_that=ssb_loaded_file)
        project.save_as_is()

    def open_scene_editor(self, filename):
        # TODO
        pass

    def open_scene_editor_for_map(self, map_name):
        # TODO
        pass

    def edit_position_mark(self, mapname: Optional[str], pos_marks: List[SourceMapPositionMark],
                           pos_mark_to_edit: int) -> bool:
        # TODO
        pass

    @property
    def _project_fm(self):
        return RomProject.get_current().get_project_file_manager()