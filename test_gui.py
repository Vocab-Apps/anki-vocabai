from typing import List
import gui
import data

class TestAnkiUtils():
    def __init__(self) -> None:
        pass

    def get_note_type_list(self) -> List[str]:
        return ['Simple', 'Chinese-Words']

    def get_field_list_for_note_type(self, note_type_name: str) -> List[str]:
        field_list_map = {
            'Simple': ['Front', 'Back'],
            'Chinese-Words': ['Simplified', 'Traditional', 'Pinyin', 'English']
        }
        return field_list_map[note_type_name]

    def get_deck_list(self) -> List[str]:
        return ['Mandarin', 'Cantonese']

def test_batch_dialog_editor_template_error(qtbot):
    
    table_import_config = data.TableImportConfig()
    anki_utils = TestAnkiUtils()

    dialog = gui.ConfigureTableImportDialog(table_import_config, anki_utils)

    # assert that dialog.note_type_combo contains the note types Simple, Chinese-Words
    assert dialog.note_type_combo.count() == 2
    assert dialog.note_type_combo.itemText(0) == 'Simple'
    assert dialog.note_type_combo.itemText(1) == 'Chinese-Words'


    # dialog.exec()