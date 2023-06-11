from dataclasses import dataclass, field
from typing import Dict

@dataclass
class TableImportConfig:
    deck_name: str = None
    note_type_name: str = None
    field_mapping: Dict[str, str] = field(default_factory=dict) # key is anki field name, value is csv field name

@dataclass
class ImportConfig:
    api_base_url: str
    username: str
    password: str
    table_configs: Dict[str, TableImportConfig]

