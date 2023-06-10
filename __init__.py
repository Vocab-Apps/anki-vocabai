import os
import sys

addon_dir = os.path.dirname(os.path.realpath(__file__))
external_dir = os.path.join(addon_dir, 'external')
sys.path.insert(0, external_dir)

import logging
import aqt
import aqt.qt
import aqt.import_export
import aqt.utils
import databind.json


from . import baserow
from . import data

logger = logging.getLogger(__name__)


def start_vocabai_import() -> None:

    # load anki addon config, and deserialize using databind
    config = aqt.mw.addonManager.getConfig(__name__)
    import_config = databind.json.load(config, data.ImportConfig)
    logger.info(import_config)

    csv_tempfile = baserow.retrieve_csv_file(import_config)

    # bring up anki csv import dialog
    aqt.import_export.importing.CsvImporter.do_import(aqt.mw, csv_tempfile.name)

def update_vocabai_config() -> None:

    # load anki addon config, and deserialize using databind
    config = aqt.mw.addonManager.getConfig(__name__)
    import_config = databind.json.load(config, data.ImportConfig)

    import_config.table_configs['106'] = data.TableImportConfig(
        deck_name='Cantonese', 
        note_type_name='Chinese-Words',
        field_mapping={'Chinese': 'Chinese', 'Jyutping': 'Romanization', 'English': 'English'})

    config = databind.json.dump(import_config, data.ImportConfig)
    aqt.mw.addonManager.writeConfig(__name__, config)

    aqt.utils.showInfo('Updated config')


import_action = aqt.qt.QAction("Import from Vocab.Ai", aqt.mw)
aqt.qt.qconnect(import_action.triggered, start_vocabai_import)
aqt.mw.form.menuTools.addAction(import_action)

import_action = aqt.qt.QAction("Import from Vocab.Ai - update config", aqt.mw)
aqt.qt.qconnect(import_action.triggered, update_vocabai_config)
aqt.mw.form.menuTools.addAction(import_action)