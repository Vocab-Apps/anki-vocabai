import pprint
import logging
import requests
import time
import tempfile
from aqt.import_export.import_csv_dialog import ImportCsvDialog
from anki.collection import (
    Collection,
    DupeResolution,
    ImportCsvRequest,
    ImportLogWithChanges,
    Progress,
)
from aqt.operations import CollectionOp, QueryOp
import aqt.utils
import aqt.progress
import aqt.import_export

logger = logging.getLogger(__name__)

# import from vocab.ai / baserow

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

# load config
config = mw.addonManager.getConfig(__name__)

def show_import_log(log_with_changes: ImportLogWithChanges) -> None:
    aqt.utils.showText(log_with_changes.log, plain_text_edit=True)

def import_progress_update(progress: Progress, update: aqt.progress.ProgressUpdate) -> None:
    if not progress.HasField("importing"):
        return
    update.label = progress.importing
    if update.user_wants_abort:
        update.abort = True

def start_vocabai_import() -> None:
    pprint.pprint(config)
    logger.info('authenticate with baserow')
    base_url = config['base_url']
    
    # authenticate with baserow
    user = config['user']
    password = config['password']
    url = f'{base_url}/api/user/token-auth/'
    response = requests.post(url, data={
        'email': user,
        'password': password
    })
    response.raise_for_status()
    token = response.json()['token']

    # start export job
    table_id = config['table_id']
    url = f'{base_url}/api/database/export/table/{table_id}/'
    logger.info(f'starting export job, url: {url}')
    response = requests.post(url, data={
        "exporter_type": "csv",
        "csv_column_separator": ",",
        "csv_include_header": True
    }, headers={
            "Authorization": f"JWT {token}"
    })
    response.raise_for_status()
    job_id = response.json()['id']

    export_finished = False

    csv_url = None
    while export_finished == False:
        # get information about the job
        url = f'{base_url}/api/database/export/{job_id}/'
        response = requests.get(url, headers={
                "Authorization": f"JWT {token}"
        })
        response.raise_for_status()
        pprint.pprint(response.json())
        export_finished = response.json()['state'] == 'finished'
        time.sleep(0.5)
    csv_url = response.json()['url']
    
    # download csv to tempfile location
    csv_tempfile = tempfile.NamedTemporaryFile(suffix='.csv', prefix='anki_vocabai_import', delete=False)
    filename = csv_tempfile.name
    with open(filename, 'w') as f:
        request_csv = requests.get(csv_url)
        f.write(request_csv.text)
    print(f'wrote csv data to {filename}')

    # bring up anki csv import dialog
    aqt.import_export.importing.CsvImporter.do_import(mw, filename)
    # def on_accepted(request: ImportCsvRequest) -> None:
    #     CollectionOp(
    #         parent=mw,
    #         op=lambda col: col.import_csv(request),
    #     ).with_backend_progress(import_progress_update).success(
    #         show_import_log
    #     ).run_in_background()

    # ImportCsvDialog(mw, filename, on_accepted)    



import_action = QAction("Import from Vocab.Ai", mw)
qconnect(import_action.triggered, start_vocabai_import)
mw.form.menuTools.addAction(import_action)