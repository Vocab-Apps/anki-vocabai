import pprint
import logging
import requests
import time
import tempfile
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


def start_vocabai_import() -> None:
    pprint.pprint(config)
    logger.info('authenticate with baserow')
    base_url = config['base_url']
    
    # authenticate with baserow
    # =========================
    user = config['user']
    password = config['password']
    url = f'{base_url}/api/user/token-auth/'
    response = requests.post(url, data={
        'email': user,
        'password': password
    })
    response.raise_for_status()
    token = response.json()['token']

    # list tables and ask user to pick one
    # ====================================

    url  = f'{base_url}/api/applications/'
    response = requests.get(url, headers={
            "Authorization": f"JWT {token}"
    })
    response.raise_for_status()
    results = response.json()
    table_ids = []
    table_names = []
    for application in results:
        application_name = application['name']
        for table in application['tables']:
            table_id = table['id']
            table_name = application_name + ' - ' + table['name']
            table_ids.append(table_id)
            table_names.append(table_name)
    pprint.pprint(table_names)

    chosen_table = aqt.utils.chooseList('Choose a table to import from', table_names)
    table_id = table_ids[chosen_table]
    print(f'chose table: {chosen_table} ({table_id})')


    # start export job
    url = f'{base_url}/api/database/export/table/{table_id}/'
    logger.info(f'starting export job, url: {url}')
    response = requests.post(url, data={
        "export_charset": "utf-8",
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
    with open(filename, 'w', encoding='utf-8') as f:
        response = requests.get(csv_url)
        csv_data = response.content.decode('utf-8')
        f.write(csv_data)
    filename = filename.replace(os.sep, '/')
    print(f'wrote csv data to {filename}')

    # bring up anki csv import dialog
    aqt.import_export.importing.CsvImporter.do_import(mw, filename)


import_action = QAction("Import from Vocab.Ai", mw)
qconnect(import_action.triggered, start_vocabai_import)
mw.form.menuTools.addAction(import_action)