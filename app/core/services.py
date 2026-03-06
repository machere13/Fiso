from pathlib import Path
from typing import Mapping

from app.core.interfaces import FileOrganizer, RulesRepository
from app.core.models import OrganizePlan, OrganizePlanItem
from app.core.rules_presets import DEFAULT_PRESET_NAME, RULE_PRESETS

class FileOrganizerService(FileOrganizer):
    def __init__(self, rules_repository: RulesRepository, preset_name: str = DEFAULT_PRESET_NAME) -> None:
        self._rules_repository = rules_repository
        self._preset_name = preset_name

    @property
    def preset_name(self) -> str:
        return self._preset_name

    @classmethod
    def available_presets(cls) -> list[str]:
        return list[str](RULE_PRESETS.keys())

    def set_preset(self, name: str) -> None:
        if name not in RULE_PRESETS:
            raise ValueError(f"Неизвестная конфигурация правил: {name}")
        self._preset_name = name

    def build_plan(self, root: Path) -> OrganizePlan:
        if not root.exists() or not root.is_dir():
            raise ValueError("Указанный путь должен быть существующей папкой")

        extensions_by_category = RULE_PRESETS[self._preset_name]

        items: list[OrganizePlanItem] = []
        for path in root.iterdir():
            if not path.is_file():
                continue
            category = self._detect_category(path.suffix, extensions_by_category)
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

    def _detect_category(self, suffix: str, extensions_by_category: Mapping[str, set[str]]) -> str | None:
        ext = suffix.lower()
        for category, exts in extensions_by_category.items():
            if ext in exts:
                return category
        return None
