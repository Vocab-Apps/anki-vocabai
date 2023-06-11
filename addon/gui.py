from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout
from typing import List
import logging
from . import anki_utils
from . import data

logger = logging.getLogger(__name__)

class ConfigureTableImportDialog(QDialog):
    UNMAPPED_FIELD_NAME = '(Unmapped)'

    def __init__(self, model: data.TableImportConfig, csv_field_names: List[str], anki_utils, parent=None):
        super().__init__(parent)
        self.csv_field_names = csv_field_names
        self.all_field_names = [self.UNMAPPED_FIELD_NAME] + csv_field_names
        self.anki_utils = anki_utils
        self.setWindowTitle("Anki Import")
        self.note_type_label = QLabel("Note Type:")
        self.note_type_combo = QComboBox()
        self.deck_label = QLabel("Deck:")
        self.deck_combo = QComboBox()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        layout = QVBoxLayout()
        layout.addWidget(self.note_type_label)
        layout.addWidget(self.note_type_combo)
        layout.addWidget(self.deck_label)
        layout.addWidget(self.deck_combo)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        # add layout for field mappings
        self.field_mappings_layout = QVBoxLayout()
        layout.addLayout(self.field_mappings_layout)
        
        self.setLayout(layout)
        self.populate_note_type_combo()
        self.populate_deck_combo()

        # populate controls based on model  
        self.load_model(model)

        self.note_type_combo.currentIndexChanged.connect(self.note_type_selected)
        self.deck_combo.currentIndexChanged.connect(self.deck_selected)

    def load_model(self, model: data.TableImportConfig):
        self.model = model

        # configure controls based on model
        if model.note_type_name != None:
            self.note_type_combo.setCurrentText(model.note_type_name)
        else:
            # ensure model gets updated with the first note type available
            self.note_type_selected()

        if model.deck_name != None:
            self.deck_combo.setCurrentText(model.deck_name)
        else:
            # ensure model gets updated with the first deck available
            self.deck_selected()


    def populate_note_type_combo(self):
        note_types = self.anki_utils.get_note_type_list()
        self.note_type_combo.addItems(note_types)

    def populate_deck_combo(self):
        decks = self.anki_utils.get_deck_list()
        self.deck_combo.addItems(decks)

    def note_type_selected(self):
        logger.debug("note_type_selected")
        note_type = self.note_type_combo.currentText()
        self.model.note_type_name = note_type
        self.note_type_fields = self.anki_utils.get_field_list_for_note_type(note_type)
        # clear all widgets from the self.field_mappings_layout layout
        for i in reversed(range(self.field_mappings_layout.count())):
            self.field_mappings_layout.itemAt(i).widget().setParent(None)
        # for each field in self.note_type_fields, add a combo box populated with self.csv_field_names
        for field in self.note_type_fields:
            label = QLabel(field)
            combo = QComboBox()
            combo.setObjectName(field)
            combo.addItems(self.all_field_names)
            if field in self.model.field_mapping:
                mapped_csv_field_name = self.model.field_mapping[field]
                if mapped_csv_field_name in self.csv_field_names:
                    combo.setCurrentText(mapped_csv_field_name)
            self.field_mappings_layout.addWidget(label)
            self.field_mappings_layout.addWidget(combo)
            # when the combo box is changed, call a lambda function which contains field
            # this will capture the current value of field in the lambda function
            combo.currentTextChanged.connect(self.get_field_mapping_text_changed_lambda(field, combo))


    def deck_selected(self):
        deck_name = self.deck_combo.currentText()
        self.model.deck_name = deck_name

    def get_field_mapping_text_changed_lambda(self, anki_field_name: str, combo: QComboBox):
        def current_text_changed(csv_field_name: str):
            if csv_field_name == self.UNMAPPED_FIELD_NAME:
                if anki_field_name in self.model.field_mapping:
                    del self.model.field_mapping[anki_field_name]
            else:
                self.model.field_mapping[anki_field_name] = csv_field_name
        return current_text_changed

    
def display_table_import_dialog(model: data.TableImportConfig, csv_field_names: List[str], parent=None) -> data.TableImportConfig:
    dialog = ConfigureTableImportDialog(model, csv_field_names, parent)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        return dialog.model
    else:
        return None