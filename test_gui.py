from typing import List
import pytest
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
        

def test_configure_table_import_dialog_defaults(qtbot):
    
    table_import_config = addon.data.TableImportConfig()
    anki_utils = TestAnkiUtils()

    csv_fieldnames = ['A', 'B', 'C']
    dialog = addon.gui.ConfigureTableImportDialog(table_import_config, csv_fieldnames, anki_utils)

    # check the model, make sure note type simple is selected, and deck is Italian
    assert dialog.model.note_type_name == 'Simple'
    assert dialog.model.deck_name == 'Italian'

    # makes sure that field_mappings_layout has been populated
    assert dialog.field_mappings_layout.count() > 0


def test_configure_baserow_config_default(qtbot):
    
    config = addon.data.BaserowConfig()

    dialog = addon.gui.ConfigureBaserowDialog(config)

    # check that the default values are correct
    assert dialog.app_vocab_radio.isChecked()
    assert dialog.config.api_base_url == 'https://app.vocab.ai'

    # switch to the baserow api url
    dialog.baserow_io_radio.setChecked(True)
    assert dialog.config.api_base_url == 'https://api.baserow.io'

    # switch to custom url
    dialog.custom_radio.setChecked(True)
    dialog.custom_edit.setText('https://custom.url')
    assert dialog.config.api_base_url == 'https://custom.url'

    # calling validate_config should throw an exception, username field is empty
    with pytest.raises(Exception):
        dialog.validate_config()

    # set username
    dialog.username_edit.setText('user@gmail.com')
    dialog.password_edit.setText('pw1')

    # calling validate_config should not throw an exception
    dialog.validate_config()
    

def test_database_table_view_dialog(qtbot):
    database_list = [
        addon.data.Database(id=1, name='db1', tables=[
            addon.data.Table(id=10, name='tableA'),
            addon.data.Table(id=11, name='tableB'),
        ]),
        addon.data.Database(id=2, name='db2', tables=[
            addon.data.Table(id=20, name='tableC'),
        ])    
    ]

    def get_view_list_fn(table: addon.data.Table):
        if table.id == 11:
            return [addon.data.View(id=100, name='view1'), addon.data.View(id=101, name='view2')]
        else:
            return []

    dialog = addon.gui.DatabaseTableViewDialog(database_list, addon.data.DatabaseTableViewConfig(), get_view_list_fn)
    
    # the default config should be db1, tableA, and empty view
    expected_databasetableviewconfig = addon.data.DatabaseTableViewConfig(
        database_id=1, table_id=10, view_id=None)
    
    assert dialog.get_config() == expected_databasetableviewconfig

    # select tableB
    dialog.table_combo.setCurrentText('tableB')
    expected_databasetableviewconfig = addon.data.DatabaseTableViewConfig(
        database_id=1, table_id=11, view_id=None)

    # select view2
    dialog.view_combo.setCurrentText('view2')
    expected_databasetableviewconfig = addon.data.DatabaseTableViewConfig(
        database_id=1, table_id=11, view_id=101)

    # select default view again
    dialog.view_combo.setCurrentText('Default')
    expected_databasetableviewconfig = addon.data.DatabaseTableViewConfig(
        database_id=1, table_id=11, view_id=None)

    # select database db2
    dialog.database_combo.setCurrentText('db2')
    # check defaults
    expected_databasetableviewconfig = addon.data.DatabaseTableViewConfig(
        database_id=2, table_id=20, view_id=None)

    # check that defaults are selected properly
    previous_selection = addon.data.DatabaseTableViewConfig(
        database_id=1, table_id=11, view_id=None)
    dialog = addon.gui.DatabaseTableViewDialog(database_list, previous_selection, get_view_list_fn)
    assert dialog.get_config() == previous_selection
    assert dialog.database_combo.currentText() == 'db1'
    assert dialog.table_combo.currentText() == 'tableB'
    assert dialog.view_combo.currentText() == 'Default'

    # put incorrect data in the defaults
    previous_selection = addon.data.DatabaseTableViewConfig(
        database_id=1, table_id=42, view_id=None)
    dialog = addon.gui.DatabaseTableViewDialog(database_list, previous_selection, get_view_list_fn)
    assert dialog.database_combo.currentText() == 'db1'
    assert dialog.table_combo.currentText() == 'tableA'
    assert dialog.view_combo.currentText() == 'Default'

    # make sure view gets defaulted
    previous_selection = addon.data.DatabaseTableViewConfig(
        database_id=1, table_id=11, view_id=100)
    dialog = addon.gui.DatabaseTableViewDialog(database_list, previous_selection, get_view_list_fn)
    assert dialog.get_config() == previous_selection
    assert dialog.database_combo.currentText() == 'db1'
    assert dialog.table_combo.currentText() == 'tableB'
    assert dialog.view_combo.currentText() == 'view1'