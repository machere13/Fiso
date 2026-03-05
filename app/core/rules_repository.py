from pathlib import Path
from typing import List

from app.core.interfaces import RulesRepository
from app.core.models import Rule

class JsonRulesRepository(RulesRepository):
    def __init__(self, path: Path) -> None:
        self._path = path

    def load_rules(self) -> List[Rule]: ...
