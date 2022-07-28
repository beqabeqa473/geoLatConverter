#__init__.py
# Copyright (C) 2012-2022 Beqa Gozalishvili <beqaprogger@gmail.com>
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
import api
import globalPluginHandler
import os
import lzma
import pickle
import queueHandler
from scriptHandler import script
import textInfos
from threading import Thread
import ui
addonHandler.initTranslation()

TABLE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "table.dat")

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = _("Georgian to latin converter")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processing = False
        self.populate_table()

    @script(
        description=_("Converts the selected text to latin alphabet."),
        gesture="kb:NVDA+L"
    )
    def script_geo2eng_selection(self, gesture):
        if self.processing:
            ui.message(_("Process is already running"))
            return
        text = self.get_selected_text()
        if not text:
            ui.message(_("no selection"))
            return
        Thread(target=self.convertText, args=[text]).start()

    @script(
        description=_("Converts the selected text to georgian alphabet."),
        gesture="kb:NVDA+G"
    )
    def script_eng2geo_selection(self, gesture):
        if self.processing:
            ui.message(_("Process is already running"))
            return
        text = self.get_selected_text()
        if not text:
            ui.message(_("no selection"))
            return
        Thread(target=self.convertText, args=[text, False]).start()

    def get_selected_text(self):
        obj = api.getCaretObject()
        try:
            info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
            if info or not info.isCollapsed:
                return info.text
        except (RuntimeError, NotImplementedError):
            return None

    def populate_table(self):
        with lzma.open(TABLE_FILE, "rb") as f:
            self.table = pickle.load(f)

    def convertText(self, text, from_geo=True):
        self.processing = True
        for key, value in self.table.items():
            text = text.replace(key, value) if from_geo else text.replace(value, key)
        queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Completed"))
        api.copyToClip(text)
        self.processing = False
