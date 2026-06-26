from dataclasses import dataclass
from typing import Callable, Any, Dict

@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]
    fn: Callable[..., Any]
