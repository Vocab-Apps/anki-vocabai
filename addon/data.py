from dataclasses import dataclass, field
from typing import Dict, Optional

API_URL_VOCABAI = 'https://app.vocab.ai'
API_URL_BASEROW = 'https://api.baserow.io'

@dataclass
class TableImportConfig:
    deck_name: str = None
    note_type_name: str = None
    field_mapping: Dict[str, str] = field(default_factory=dict) # key is anki field name, value is csv field name

@dataclass
class DatabaseTableViewConfig:
    database_id: int = None
    table_id: int = None
    view_id: int = None

@dataclass
class BaserowConfig:
    api_base_url: str = 'https://app.vocab.ai'
    username: str = None
    password: str = None

    def validate(self):
        if not self.api_base_url:
            raise ValueError("API base URL is not set")
        if not self.username:
            raise ValueError("Username is not set")
        if not self.password:
            raise ValueError("Password is not set")
        if self.username.strip() == "":
            raise ValueError("Username is empty")
        if self.password.strip() == "":
            raise ValueError("Password is empty")

@dataclass
class ImportConfig:
    baserow_config: BaserowConfig = field(default_factory=BaserowConfig)
    table_configs: Dict[str, TableImportConfig] = field(default_factory=dict)
    last_import_table_id: Optional[int] = None

@dataclass
class Table:
    id: int
    name: str

@dataclass
class Database:
    id: int
    name: str
    tables: list[Table]

@dataclass
class View:
    id: int
    name: str