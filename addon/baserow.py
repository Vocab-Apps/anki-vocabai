from . import data
import logging
import requests
import tempfile
import time
import os
import aqt.utils

logger = logging.getLogger(__name__)

# given a data.ImportConfig object, return a named temporary file containing the CSV data, and the table_id
def retrieve_csv_file(import_config: data.ImportConfig) -> tempfile.NamedTemporaryFile:
    logger.info('authenticate with baserow')
    base_url = import_config.api_base_url
    
    # authenticate with baserow
    # =========================
    url = f'{base_url}/api/user/token-auth/'
    response = requests.post(url, data={
        'email': import_config.username,
        'password': import_config.password
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

    startrow = 0
    if import_config.last_import_table_id != None:
        startrow = table_ids.index(import_config.last_import_table_id)
    chosen_table = aqt.utils.chooseList('Choose a table to import from', table_names, startrow=startrow)
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
        # pprint.pprint(response.json())
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
    logger.info(f'wrote csv data to {filename}')

    return csv_tempfile, table_id

