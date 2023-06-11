from typing import List
import addon.gui
import addon.data

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
        return ['Italian', 'Mandarin', 'Cantonese']

def test_configure_table_import_dialog(qtbot):
    
    table_import_config = addon.data.TableImportConfig()
    anki_utils = TestAnkiUtils()

    csv_fieldnames = ['Chinese', 'Jyutping', 'English']
    dialog = addon.gui.ConfigureTableImportDialog(table_import_config, csv_fieldnames, anki_utils)

    # assert that dialog.note_type_combo contains the note types Simple, Chinese-Words
    all_note_types = [dialog.note_type_combo.itemText(i) for i in range(dialog.note_type_combo.count())]
    assert all_note_types == ['Simple', 'Chinese-Words']

    # assert that dialog.deck_combo contains the decks Italian, Mandarin, Cantonese
    all_decks = [dialog.deck_combo.itemText(i) for i in range(dialog.deck_combo.count())]
    assert all_decks == ['Italian', 'Mandarin', 'Cantonese']

def test_configure_table_import_dialog_choose_note_type(qtbot):
    
    table_import_config = addon.data.TableImportConfig()
    anki_utils = TestAnkiUtils()

    csv_fieldnames = ['Chinese', 'Jyutping', 'English']
    dialog = addon.gui.ConfigureTableImportDialog(table_import_config, csv_fieldnames, anki_utils)

    dialog.note_type_combo.setCurrentText('Chinese-Words')
    assert dialog.model.note_type_name == 'Chinese-Words'

    dialog.note_type_combo.setCurrentText('Simple')
    assert dialog.model.note_type_name == 'Simple'
