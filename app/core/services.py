from pathlib import Path
from typing import Dict, Set

from app.core.interfaces import FileOrganizer, RulesRepository
from app.core.models import OrganizePlan, OrganizePlanItem

class FileOrganizerService(FileOrganizer):
    _CATEGORY_EXTENSIONS: Dict[str, Set[str]] = {
        "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"},
        "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv"},
        "Audios": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
    }

    def __init__(self, rules_repository: RulesRepository) -> None:
        self._rules_repository = rules_repository

    def build_plan(self, root: Path) -> OrganizePlan:
        if not root.exists() or not root.is_dir():
            raise ValueError("Указанный путь должен быть существующей папкой")

        items: list[OrganizePlanItem] = []
        for path in root.iterdir():
            if not path.is_file():
                continue
            category = self._detect_category(path.suffix)
            if category is None:
                continue
            target_dir = root / category
            target = target_dir / path.name
            if target == path:
                continue
            items.append(OrganizePlanItem(source=path, destination=target))

        return OrganizePlan(root=root, items=items)

    def apply_plan(self, plan: OrganizePlan) -> None:
        for item in plan.items:
            item.destination.parent.mkdir(parents=True, exist_ok=True)
            item.source.rename(item.destination)

    def _detect_category(self, suffix: str) -> str | None:
        ext = suffix.lower()
        for category, exts in self._CATEGORY_EXTENSIONS.items():
            if ext in exts:
                return category
        return None
