from dataclasses import dataclass
from typing import Dict

@dataclass
class TableImportConfig:
    table_id: str
    deck_name: str
    note_type_name: str

@dataclass
class ImportConfig:
    api_base_url: str
    username: str
    password: str
    table_configs: Dict[str, TableImportConfig]

