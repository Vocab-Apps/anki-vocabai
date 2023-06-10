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
import aqt.operations
import anki.collection


from . import baserow
from . import data
from . import logic

logger = logging.getLogger(__name__)

def get_config() -> data.ImportConfig:
    config = aqt.mw.addonManager.getConfig(__name__)
    import_config = databind.json.load(config, data.ImportConfig)
    return import_config

def start_vocabai_import_manual() -> None:
    import_config = get_config()
    logger.info(import_config)

    csv_tempfile, table_id = baserow.retrieve_csv_file(import_config)

    # bring up anki csv import dialog
    aqt.import_export.importing.CsvImporter.do_import(aqt.mw, csv_tempfile.name)

def start_vocabai_import_automatic() -> None:
    import_config = get_config()
    logger.info(import_config)

    csv_tempfile, table_id = baserow.retrieve_csv_file(import_config)

    # create the csv import request
    table_import_config = import_config.table_configs[str(table_id)]
    request = logic.create_import_csv_request(csv_tempfile.name, table_import_config)

    aqt.operations.CollectionOp(
        parent=aqt.mw,
        op=lambda col: col.import_csv(request),
    ).with_backend_progress(aqt.import_export.importing.import_progress_update).success(
        aqt.import_export.importing.show_import_log
    ).run_in_background()    

def update_vocabai_config() -> None:
    import_config = get_config()

    import_config.table_configs['106'] = data.TableImportConfig(
        deck_name='Cantonese', 
        note_type_name='Chinese-Words',
        field_mapping={'Chinese': 'Chinese', 'Jyutping': 'Romanization', 'English': 'English'})

    config = databind.json.dump(import_config, data.ImportConfig)
    aqt.mw.addonManager.writeConfig(__name__, config)

    aqt.utils.showInfo('Updated config')


import_action = aqt.qt.QAction("Import from Vocab.Ai - manual", aqt.mw)
aqt.qt.qconnect(import_action.triggered, start_vocabai_import_manual)
aqt.mw.form.menuTools.addAction(import_action)

import_action = aqt.qt.QAction("Import from Vocab.Ai - automatic", aqt.mw)
aqt.qt.qconnect(import_action.triggered, start_vocabai_import_automatic)
aqt.mw.form.menuTools.addAction(import_action)

import_action = aqt.qt.QAction("Import from Vocab.Ai - update config", aqt.mw)
aqt.qt.qconnect(import_action.triggered, update_vocabai_config)
aqt.mw.form.menuTools.addAction(import_action)