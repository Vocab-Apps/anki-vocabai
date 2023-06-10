from dataclasses import dataclass
from typing import Dict

@dataclass
class TableImportConfig:
    deck_name: str
    note_type_name: str
    field_mapping: Dict[str, str] # key is anki field name, value is csv field name

@dataclass
class ImportConfig:
    api_base_url: str
    username: str
    password: str
    table_configs: Dict[str, TableImportConfig]

