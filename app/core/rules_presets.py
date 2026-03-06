from typing import Dict, Set

from app.core.file_categories import CATEGORY_EXTENSIONS

ExtensionsMap = Dict[str, Set[str]]

# пресеты, временно, потом динамически сделаю
RULE_PRESETS: dict[str, ExtensionsMap] = {
    "Media (Images/Videos/Audios)": CATEGORY_EXTENSIONS,
    "Images only": {
        "Images": CATEGORY_EXTENSIONS["Images"],
    },
    "Videos only": {
        "Videos": CATEGORY_EXTENSIONS["Videos"],
    },
    "Audios only": {
        "Audios": CATEGORY_EXTENSIONS["Audios"],
    },
}

DEFAULT_PRESET_NAME = "Media (Images/Videos/Audios)"

