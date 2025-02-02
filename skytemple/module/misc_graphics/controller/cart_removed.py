#  Copyright 2020-2021 Capypara and the SkyTemple Contributors
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
import logging
import os
import sys
from typing import TYPE_CHECKING, Optional, Dict

import cairo

from skytemple.core.error_handler import display_error
from skytemple.core.message_dialog import SkyTempleMessageDialog
from skytemple.core.ui_utils import add_dialog_png_filter

from PIL import Image
from gi.repository import Gtk
from gi.repository.Gtk import ResponseType

from skytemple.controller.main import MainController
from skytemple.core.img_utils import pil_to_cairo_surface
from skytemple.core.module_controller import AbstractController
from skytemple_files.common.i18n_util import f, _

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from skytemple.module.misc_graphics.module import MiscGraphicsModule

class CartRemovedController(AbstractController):
    def __init__(self, module: 'MiscGraphicsModule', _: str):
        self.module = module
        
        self.builder: Optional[Gtk.Builder] = None

    def get_view(self) -> Gtk.Widget:
        self.builder = self._get_builder(__file__, 'cart_removed.glade')

        self._reinit_image()
        
        self.builder.connect_signals(self)
        self.builder.get_object('draw').connect('draw', self.draw)
        return self.builder.get_object('editor')

    def on_cart_removed_info_clicked(self, *args):
        md = SkyTempleMessageDialog(
            MainController.window(),
            Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            _("This is what the game shows when the cartridge is removed while playing.\n"
              "IMPORTANT! The game stores this compressed in the ARM9, so this is limited in space.\n"
              "It is recommended to only edit this to change the text color/content."),
            title=_("Cartridge Removed Image Info")
        )
        md.run()
        md.destroy()
    
    def on_export_clicked(self, w: Gtk.MenuToolButton):
        dialog = Gtk.FileChooserNative.new(
            _("Export image as PNG..."),
            MainController.window(),
            Gtk.FileChooserAction.SAVE,
            _("_Save"), None
        )

        add_dialog_png_filter(dialog)

        response = dialog.run()
        fn = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.ACCEPT:
            if '.' not in fn:
                fn += '.png'
            self.module.get_cart_removed_data().save(fn)
    def on_import_clicked(self, w: Gtk.MenuToolButton):
        dialog = Gtk.FileChooserNative.new(
            _("Import image as PNG..."),
            MainController.window(),
            Gtk.FileChooserAction.OPEN,
            _("_Open"), None
        )

        add_dialog_png_filter(dialog)

        response = dialog.run()
        fn = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.ACCEPT:
            try:
                img = Image.open(fn, 'r')
                self.module.set_cart_removed_data(img)
            except Exception as err:
                display_error(
                    sys.exc_info(),
                    str(err),
                    _("Error importing cart removed image.")
                )
            self._reinit_image()

    def _reinit_image(self):
        surface = self.module.get_cart_removed_data()
        self.surface = pil_to_cairo_surface(surface.convert('RGBA'))
        self.builder.get_object('draw').queue_draw()
    
    def draw(self, wdg, ctx: cairo.Context, *args):
        if self.surface:
            wdg.set_size_request(self.surface.get_width(), self.surface.get_height())
            ctx.fill()
            ctx.set_source_surface(self.surface, 0, 0)
            ctx.get_source().set_filter(cairo.Filter.NEAREST)
            ctx.paint()
        return True
