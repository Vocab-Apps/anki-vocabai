from . import data
import logging
import requests
import tempfile
import time
import os
import aqt.utils

logger = logging.getLogger(__name__)

def retrieve_authentication_token(import_config: data.ImportConfig) -> str:
    logger.info('authenticate with baserow')
    base_url = import_config.baserow_config.api_base_url
    
    # authenticate with baserow
    # =========================
    url = f'{base_url}/api/user/token-auth/'
    response = requests.post(url, data={
        'email': import_config.baserow_config.username,
        'password': import_config.baserow_config.password
    })
    response.raise_for_status()
    token = response.json()['token']
    return token


# given an ImportConfig and Table object, return a list of Views
def get_view_list(import_config: data.ImportConfig, table: data.Table) -> list[data.View]:
    token = retrieve_authentication_token(import_config)
    url = f'{import_config.baserow_config.api_base_url}/api/database/views/table/{table.id}/'
    token = retrieve_authentication_token(import_config)
    response = requests.get(url, headers={
            "Authorization": f"JWT {token}"
    })
    response.raise_for_status()
    results = response.json()
    view_list = []
    for view in results:
        view = data.View(id=view['id'], name=view['name'])
        view_list.append(view)
    return view_list

# given an authentication token, return a list of data.Database objects
def build_database_list(import_config: data.ImportConfig) -> list[data.Database]:

    token = retrieve_authentication_token(import_config)

    url  = f'{import_config.baserow_config.api_base_url}/api/applications/'
    response = requests.get(url, headers={
            "Authorization": f"JWT {token}"
    })
    response.raise_for_status()
    results = response.json()
    database_list = []
    for application in results:
        database = data.Database(id=application['id'], name=application['name'], tables=[])
        application_name = application['name']
        for table in application['tables']:
            table = data.Table(id=table['id'], name=table['name'])
            database.tables.append(table)
        database_list.append(database)
    return database_list

# given a data.ImportConfig object, return a named temporary file containing the CSV data, and the table_id
def retrieve_csv_file(import_config: data.ImportConfig, database_table_view_config: data.DatabaseTableViewConfig) -> tempfile.NamedTemporaryFile:
    logger.info('authenticate with baserow')
    base_url = import_config.baserow_config.api_base_url
    
    token = retrieve_authentication_token(import_config)

    # start export job
    url = f'{base_url}/api/database/export/table/{database_table_view_config.table_id}/'
    logger.info(f'starting export job, url: {url}')
    data = {
        "export_charset": "utf-8",
        "exporter_type": "csv",
        "csv_column_separator": ",",
        "csv_include_header": True
    }
    if database_table_view_config.view_id != None:
        data['view_id'] = database_table_view_config.view_id
    response = requests.post(url, data=data, headers={
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

    return csv_tempfile

