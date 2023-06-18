

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
from . import csv_utils
from . import gui
from . import anki_utils

logger = logging.getLogger(__name__)

def initialize():
    def get_config() -> data.ImportConfig:
        config = aqt.mw.addonManager.getConfig(__name__)
        import_config = databind.json.load(config, data.ImportConfig)
        return import_config

    def write_config(import_config: data.ImportConfig) -> None:
        config = databind.json.dump(import_config, data.ImportConfig)
        aqt.mw.addonManager.writeConfig(__name__, config)


    def start_vocabai_import_automatic() -> None:
        anki_util_instance = anki_utils.AnkiUtils()
        import_config = get_config()
        logger.info(import_config)

        try:
            # check that baserow config is valid
            try:
                import_config.baserow_config.validate()
            except Exception as e:
                raise Exception(f'Missing configuration: {str(e)}, please run configuration.')

            # get database list
            database_list = baserow.build_database_list(import_config)
            def build_get_view_list_fn(import_config: data.ImportConfig):
                def get_view_list(table: data.Table):
                    return baserow.get_view_list(import_config, table)
                return get_view_list
            database_table_view_config = gui.display_database_table_view_dialog(database_list, import_config.last_import, build_get_view_list_fn(import_config))
            if database_table_view_config == None:
                # user canceled
                return

            csv_tempfile = baserow.retrieve_csv_file(import_config, database_table_view_config)

            table_import_config = data.TableImportConfig()
            if database_table_view_config.get_key() in import_config.table_configs:
                table_import_config = import_config.table_configs[database_table_view_config.get_key()]

            
            csv_field_names = csv_utils.get_fieldnames(csv_tempfile.name)
            table_import_config = gui.display_table_import_dialog(table_import_config, csv_field_names, anki_util_instance)
            if table_import_config == None:
                # user canceled
                return

            # create the csv import request
            request, csv_tempfile_no_header = logic.create_import_csv_request(csv_tempfile.name, table_import_config)
        except Exception as e:
            logger.exception(e)
            aqt.utils.showCritical(f"Error while importing from Baserow: {str(e)}", aqt.mw)
            return

        # save table_import_config
        import_config.last_import = database_table_view_config
        import_config.table_configs[database_table_view_config.get_key()] = table_import_config
        write_config(import_config)

        aqt.operations.CollectionOp(
            parent=aqt.mw,
            op=lambda col: col.import_csv(request),
        ).with_backend_progress(aqt.import_export.importing.import_progress_update).success(
            aqt.import_export.importing.show_import_log
        ).run_in_background()    


    def display_baserow_config_dialog():
        import_config = get_config()
        baserow_config = import_config.baserow_config
        baserow_config = gui.display_baserow_config_dialog(baserow_config)
        if baserow_config == None:
            # user canceled, don't persist config
            return

        import_config.baserow_config = baserow_config
        write_config(import_config)


    import_action = aqt.qt.QAction("Vocab.Ai / Baserow: Start Import", aqt.mw)
    aqt.qt.qconnect(import_action.triggered, start_vocabai_import_automatic)
    aqt.mw.form.menuTools.addAction(import_action)

    # add menu entry for baserow config
    config_action = aqt.qt.QAction("Vocab.Ai / Baserow: Configure", aqt.mw)
    aqt.qt.qconnect(config_action.triggered, display_baserow_config_dialog)
    aqt.mw.form.menuTools.addAction(config_action)