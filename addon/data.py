from dataclasses import dataclass, field
from typing import Dict, Optional

API_URL_VOCABAI = 'https://words.vocab.ai'
API_URL_BASEROW = 'https://api.baserow.io'
API_URL_VOCABAI_OLD = 'https://app.vocab.ai'

@dataclass
class TableImportConfig:
    deck_name: str = None
    note_type_name: str = None
    field_mapping: Dict[str, str] = field(default_factory=dict) # key is anki field name, value is csv field name

@dataclass(eq=True, frozen=True)
class DatabaseTableViewConfig:
    database_id: Optional[int] = None
    table_id: Optional[int] = None
    view_id: Optional[int] = None

    def get_key(self):
        key = f'database_{self.database_id}_table_{self.table_id}'
        if self.view_id:
            key += f'_view_{self.view_id}'
        return key

@dataclass
class BaserowConfig:
    api_base_url: str = API_URL_VOCABAI
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
    last_import: Optional[DatabaseTableViewConfig] = field(default_factory=DatabaseTableViewConfig)

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