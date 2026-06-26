from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Skill:
    name: str
    description: str
    instructions: str
    scripts_path: Optional[Path] = None
