from PyQt6.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout
from . import anki_utils
from . import data

class ConfigureTableImportDialog(QDialog):
    def __init__(self, model: data.TableImportConfig, anki_utils, parent=None):
        super().__init__(parent)
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
        fields = self.anki_utils.get_field_list_for_note_type(note_type)
        self.field_combo.clear()
        self.field_combo.addItems(fields)

    def deck_selected(self):
        deck_name = self.deck_combo.currentText()
        self.model.deck_name = deck_name

    
def display_table_import_dialog_get_table_import_config(model: data.TableImportConfig, parent=None) -> data.TableImportConfig:
    dialog = ConfigureTableImportDialog(model, parent)
    result = dialog.exec_()
    if result == QDialog.Accepted:
        return dialog.model
    else:
        return None