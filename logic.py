import anki.import_export_pb2
from . import data

# given a data.TableImportConfig object, create a new anki.collection.ImportCsvRequest object
def create_import_csv_request(csv_file_path: str, table_import_config: data.TableImportConfig) -> anki.import_export_pb2.ImportCsvRequest:
    request = anki.import_export_pb2.ImportCsvRequest()
    request.path = csv_file_path
    # request.metadata is of type anki.import_export_pb2.CsvMetadata
    request.metadata.delimiter = anki.import_export_pb2.CsvMetadata.Delimiter.COMMA
    
    
