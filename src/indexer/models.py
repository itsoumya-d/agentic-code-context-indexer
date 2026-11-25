from dataclasses import dataclass, field
from typing import List, Set

@dataclass
class SymbolNode:
    name: str
    symbol_type: str  # function, class, method
    file_path: str
    line_start: int
    line_end: int
    signature: str
    docstring: str = ""
    dependencies: Set[str] = field(default_factory=set)
    content: str = ""
    estimated_tokens: int = 0

@dataclass
class ContextManifest:
    target_symbol: str
    budget_tokens: int
    used_tokens: int
    included_symbols: List[str]
    context_text: str
