from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from app.core.models import OrganizePlan, Rule

class RulesRepository(ABC):
    @abstractmethod
    def load_rules(self) -> List[Rule]: ...

class FileOrganizer(ABC):
    @abstractmethod
    def build_plan(self, root: Path) -> OrganizePlan: ...

    @abstractmethod
    def apply_plan(self, plan: OrganizePlan) -> None: ...
