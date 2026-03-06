# временный файл
from typing import Dict, Set

CATEGORY_EXTENSIONS: Dict[str, Set[str]] = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv"},
    "Audios": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
}
