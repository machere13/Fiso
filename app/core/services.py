from pathlib import Path

from app.core.interfaces import FileOrganizer, RulesRepository
from app.core.models import OrganizePlan

class FileOrganizerService(FileOrganizer):
    def __init__(self, rules_repository: RulesRepository) -> None:
        self._rules_repository = rules_repository

    def build_plan(self, root: Path) -> OrganizePlan: ...

    def apply_plan(self, plan: OrganizePlan) -> None: ...
