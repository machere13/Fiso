import json
from pathlib import Path
from typing import Dict, Set

from app.core.rules_presets import ExtensionsMap

_USER_PRESETS_PATH = Path(__file__).resolve().parent.parent.parent / "user_presets.json"

def _normalize_ext(ext: str) -> str:
    ext = ext.strip().lower()
    if ext and not ext.startswith("."):
        ext = "." + ext
    return ext


def load_user_presets() -> Dict[str, ExtensionsMap]:
    if not _USER_PRESETS_PATH.exists():
        return {}
    try:
        data = json.loads(_USER_PRESETS_PATH.read_text(encoding="utf-8"))
        result: Dict[str, ExtensionsMap] = {}
        for name, categories in data.items():
            result[name] = {
                cat: {_normalize_ext(e) for e in exts}
                for cat, exts in categories.items()
            }
        return result
    except (json.JSONDecodeError, TypeError):
        return {}


def save_user_preset(name: str, mapping: ExtensionsMap) -> None:
    data: Dict[str, Dict[str, list]] = {}
    if _USER_PRESETS_PATH.exists():
        try:
            data = json.loads(_USER_PRESETS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            pass
    data[name] = {cat: sorted(exts) for cat, exts in mapping.items()}
    _USER_PRESETS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def delete_user_preset(name: str) -> None:
    if not _USER_PRESETS_PATH.exists():
        return
    try:
        data = json.loads(_USER_PRESETS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, TypeError):
        return
    data.pop(name, None)
    if data:
        _USER_PRESETS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        _USER_PRESETS_PATH.unlink(missing_ok=True)
