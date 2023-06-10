import anki.import_export_pb2
import aqt
from . import data

def get_note_type_fieldnames(model_id):
    # for the anki note type, build an index from the field name to the field index
    model = aqt.mw.col.models.get(model_id)
    fields = model['flds']
    field_names = [x['name'] for x in fields]
    return field_names

def get_csv_file_fieldname_to_index(csv_file_path: str):
    # get the list of fields in the csv_file_path CSV file
    with open(csv_file_path, 'r') as csv_file:
        csv_header = csv_file.readline()
        csv_fields = csv_header.split(',')
        csv_fields = [x.strip() for x in csv_fields]

        # create dict which maps field name to field index
        field_name_to_index = {field_name: index for index, field_name in enumerate(csv_fields)}
        return field_name_to_index

# given a data.TableImportConfig object, create a new anki.collection.ImportCsvRequest object
def create_import_csv_request(csv_file_path: str, table_import_config: data.TableImportConfig) -> anki.import_export_pb2.ImportCsvRequest:
    request = anki.import_export_pb2.ImportCsvRequest()
    request.path = csv_file_path
    # request.metadata is of type anki.import_export_pb2.CsvMetadata
    request.metadata.delimiter = anki.import_export_pb2.CsvMetadata.Delimiter.COMMA
    request.metadata.dupe_resolution = anki.import_export_pb2.CsvMetadata.DupeResolution.UPDATE
    request.metadata.match_scope = anki.import_export_pb2.CsvMetadata.MatchScope.NOTETYPE_AND_DECK

    # set deck
    deck_id = aqt.mw.col.decks.id_for_name(table_import_config.deck_name)
    request.metadata.deck_id = deck_id
    # set note type
    model_id = aqt.mw.col.models.id_for_name(table_import_config.note_type_name)
    request.metadata.global_notetype.id = model_id

    # add field mapping
    anki_field_names = get_note_type_fieldnames(model_id)
    csv_field_name_to_index_map = get_csv_file_fieldname_to_index(csv_file_path)

    for anki_field_name in anki_field_names:
        # populate request.metadata.global_notetype.field_columns
        # for each anki_field_name, push the 1-based index of the field in the CSV file, or 0 if unmapped
        mapped_csv_field_name = table_import_config.field_mapping.get(anki_field_name, None)
        if mapped_csv_field_name is None:
            request.metadata.global_notetype.field_columns.append(0)
        else:
            csv_field_name_index = csv_field_name_to_index_map[mapped_csv_field_name] + 1
            request.metadata.global_notetype.field_columns.append(csv_field_name_index)


    return request