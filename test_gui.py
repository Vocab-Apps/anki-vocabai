from typing import List
import logging
import addon.gui
import addon.data
from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout

logger = logging.getLogger(__name__)

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

def test_configure_table_import_dialog_choose_deck(qtbot):
    
    table_import_config = addon.data.TableImportConfig()
    anki_utils = TestAnkiUtils()

    csv_fieldnames = ['Chinese', 'Jyutping', 'English']
    dialog = addon.gui.ConfigureTableImportDialog(table_import_config, csv_fieldnames, anki_utils)

    dialog.deck_combo.setCurrentText('Cantonese')
    assert dialog.model.deck_name == 'Cantonese'

    # now set the deck to Italian
    dialog.deck_combo.setCurrentText('Italian')
    assert dialog.model.deck_name == 'Italian'

def test_configure_table_import_dialog_field_mapping(qtbot):
    table_import_config = addon.data.TableImportConfig()
    anki_utils = TestAnkiUtils()

    csv_fieldnames = ['A', 'B', 'C']
    dialog = addon.gui.ConfigureTableImportDialog(table_import_config, csv_fieldnames, anki_utils)

    # pick note type Chinese-Words
    dialog.note_type_combo.setCurrentText('Chinese-Words')

    # we have 3 csv fields, each combox box representing an anki field should have 4 entries
    simplified_combobox = dialog.findChild(QComboBox, 'Simplified')
    assert [simplified_combobox.itemText(i) for i in range(simplified_combobox.count())] == [
        dialog.UNMAPPED_FIELD_NAME, 'A', 'B', 'C']

    # choose field B
    simplified_combobox.setCurrentText('B')

    assert dialog.model.field_mapping == {'Simplified': 'B'}

    # find the Traditional combobox, and set it to C
    traditional_combobox = dialog.findChild(QComboBox, 'Traditional')
    traditional_combobox.setCurrentText('C')
    # check that field_mapping is now correct
    assert dialog.model.field_mapping == {'Simplified': 'B', 'Traditional': 'C'}

    # now, unmap the Simplified field
    simplified_combobox.setCurrentText(dialog.UNMAPPED_FIELD_NAME)
    assert dialog.model.field_mapping == {'Traditional': 'C'}
        
