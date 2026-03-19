from app.core.rules_presets import RULE_PRESETS, ExtensionsMap
from app.core.user_presets import (
    delete_user_preset,
    load_user_presets,
    save_user_preset,
)


def get_all_presets() -> dict[str, ExtensionsMap]:
    return {**RULE_PRESETS, **load_user_presets()}


def is_builtin(name: str) -> bool:
    return name in RULE_PRESETS


def add_user_preset(name: str, mapping: ExtensionsMap) -> None:
    if is_builtin(name):
        raise ValueError("Нельзя переопределить встроенную конфигурацию")
    save_user_preset(name, mapping)


def remove_user_preset(name: str) -> None:
    if is_builtin(name):
        return
    delete_user_preset(name)
