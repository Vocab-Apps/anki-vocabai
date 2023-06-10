import os
import sys

addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')
sys.path.insert(0, external_dir)

import logging
import aqt
import aqt.qt
import aqt.import_export
import databind.json



from . import baserow
from . import data

logger = logging.getLogger(__name__)


# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

# load config

def start_vocabai_import() -> None:

    config = aqt.mw.addonManager.getConfig(__name__)
    import_config = databind.json.load(config, data.ImportConfig)

    csv_tempfile = baserow.retrieve_csv_file(import_config)

    # bring up anki csv import dialog
    aqt.import_export.importing.CsvImporter.do_import(aqt.mw, csv_tempfile.name)


import_action = aqt.qt.QAction("Import from Vocab.Ai", aqt.mw)
aqt.qt.qconnect(import_action.triggered, start_vocabai_import)
aqt.mw.form.menuTools.addAction(import_action)