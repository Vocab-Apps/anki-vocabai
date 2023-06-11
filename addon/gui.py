from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout
from typing import List
from . import anki_utils
from . import data

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
        self.ok_button.clicked.connect(self.accept)
        layout = QVBoxLayout()
        layout.addWidget(self.note_type_label)
        layout.addWidget(self.note_type_combo)
        layout.addWidget(self.deck_label)
        layout.addWidget(self.deck_combo)
        layout.addWidget(self.ok_button)

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
        # configure controls based on model
        self.note_type_combo.setCurrentText(model.note_type_name)
        self.deck_combo.setCurrentText(model.deck_name)
        self.model = model

    def populate_note_type_combo(self):
        note_types = self.anki_utils.get_note_type_list()
        self.note_type_combo.addItems(note_types)

    def populate_deck_combo(self):
        decks = self.anki_utils.get_deck_list()
        self.deck_combo.addItems(decks)

    def note_type_selected(self):
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
            combo.currentIndexChanged.connect(lambda field=field: self.field_mapping_selected(field, combo))


    def deck_selected(self):
        deck_name = self.deck_combo.currentText()
        self.model.deck_name = deck_name

    def field_mapping_selected(self, field, combo):
        # update the model with the new field mapping
        csv_field_name = combo.currentText()
        if csv_field_name == self.UNMAPPED_FIELD_NAME:
            if field in self.model.field_mapping:
                del self.model.field_mapping[field]
        else:
            self.model.field_mapping[field] = csv_field_name


    
def display_table_import_dialog_get_table_import_config(model: data.TableImportConfig, parent=None) -> data.TableImportConfig:
    dialog = ConfigureTableImportDialog(model, parent)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        return dialog.model
    else:
        return None