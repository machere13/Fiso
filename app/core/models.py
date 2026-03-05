from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

@dataclass
class Rule:
    name: str
    conditions: Dict[str, str]
    target_subdir: str

@dataclass
class OrganizePlanItem:
    source: Path
    destination: Path

@dataclass
class OrganizePlan:
    root: Path
    items: List[OrganizePlanItem]
