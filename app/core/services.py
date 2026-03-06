from pathlib import Path
from typing import Mapping

from app.core.interfaces import FileOrganizer, RulesRepository
from app.core.models import OrganizePlan, OrganizePlanItem
from app.core.preset_registry import get_all_presets
from app.core.rules_presets import DEFAULT_PRESET_NAME


class FileOrganizerService(FileOrganizer):
    def __init__(self, rules_repository: RulesRepository, preset_name: str = DEFAULT_PRESET_NAME) -> None:
        self._rules_repository = rules_repository
        self._preset_name = preset_name
        self._include_subfolders = False

    @property
    def preset_name(self) -> str:
        return self._preset_name

    @classmethod
    def available_presets(cls) -> list[str]:
        return list[str](get_all_presets().keys())

    def set_preset(self, name: str) -> None:
        if name not in get_all_presets():
            raise ValueError(f"Неизвестная конфигурация правил: {name}")
        self._preset_name = name

    def set_include_subfolders(self, value: bool) -> None:
        self._include_subfolders = value

    def build_plan(self, root: Path) -> OrganizePlan:
        if not root.exists() or not root.is_dir():
            raise ValueError("Указанный путь должен быть существующей папкой")

        presets = get_all_presets()
        if self._preset_name not in presets:
            self._preset_name = DEFAULT_PRESET_NAME
        extensions_by_category = presets[self._preset_name]
        items: list[OrganizePlanItem] = []
        reserved_destinations: set[Path] = set[Path]()

        if self._include_subfolders:
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                category = self._detect_category(path.suffix, extensions_by_category)
                if category is None:
                    continue
                target_dir = root / category
                if path.parent == target_dir:
                    continue
                target = self._unique_path(target_dir, path.name, reserved_destinations)
                if target.resolve() == path.resolve():
                    continue
                items.append(OrganizePlanItem(source=path, destination=target))
                reserved_destinations.add(target)
        else:
            for path in root.iterdir():
                if not path.is_file():
                    continue
                category = self._detect_category(path.suffix, extensions_by_category)
                if category is None:
                    continue
                target_dir = root / category
                target = self._unique_path(target_dir, path.name, reserved_destinations)
                if target == path:
                    continue
                items.append(OrganizePlanItem(source=path, destination=target))
                reserved_destinations.add(target)

        return OrganizePlan(root=root, items=items)

    def _unique_path(self, directory: Path, name: str, reserved_destinations: set[Path]) -> Path:
        target = directory / name
        if not target.exists() and target not in reserved_destinations:
            return target
        stem = Path(name).stem
        suffix = Path(name).suffix
        n = 1
        while True:
            target = directory / f"{stem} ({n}){suffix}"
            if not target.exists() and target not in reserved_destinations:
                return target
            n += 1

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
