from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel


class MetaInfo(BaseModel):
    files_hashes: Dict[str, str] = {}

    def get_hash_for_file(self, file_path: Path) -> Optional[str]:
        return self.files_hashes.get(str(file_path), None)

    def add_hash_for_file(self, file_path: Path, file_hash: str) -> None:
        self.files_hashes[str(file_path)] = file_hash

    def clear_files_hashes(self) -> None:
        self.files_hashes.clear()

    def replace_files_hashes(self, files_hashes: Dict[str, str]) -> None:
        self.clear_files_hashes()
        self.files_hashes.update(files_hashes)
