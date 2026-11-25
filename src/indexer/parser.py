import ast
from typing import Dict, List, Set, Optional
from .models import SymbolNode, ContextManifest

class CodeASTIndexer:
    def __init__(self):
        self.symbols: Dict[str, SymbolNode] = {}

    def parse_source(self, code: str, file_path: str) -> List[SymbolNode]:
        tree = ast.parse(code, filename=file_path)
        lines = code.splitlines()
        found: List[SymbolNode] = []

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                sym_type = "class" if isinstance(node, ast.ClassDef) else "function"
                start = node.lineno
                end = node.end_lineno or start
                content = "\n".join(lines[start - 1 : end])
                doc = ast.get_docstring(node) or ""

                # Extract dependencies (called names)
                calls: Set[str] = set()
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        if isinstance(sub.func, ast.Name):
                            calls.add(sub.func.id)
                        elif isinstance(sub.func, ast.Attribute):
                            calls.add(sub.func.attr)

                sig_line = lines[start - 1].strip()
                tokens = max(1, len(content) // 4)

                sym = SymbolNode(
                    name=node.name,
                    symbol_type=sym_type,
                    file_path=file_path,
                    line_start=start,
                    line_end=end,
                    signature=sig_line,
                    docstring=doc,
                    dependencies=calls,
                    content=content,
                    estimated_tokens=tokens
                )
                self.symbols[node.name] = sym
                found.append(sym)

        return found

    def assemble_context(self, target_name: str, token_budget: int) -> ContextManifest:
        if target_name not in self.symbols:
            return ContextManifest(
                target_symbol=target_name,
                budget_tokens=token_budget,
                used_tokens=0,
                included_symbols=[],
                context_text=""
            )

        target = self.symbols[target_name]
        queue: List[SymbolNode] = [target]
        visited: Set[str] = {target.name}

        # Gather 1-hop and 2-hop dependencies
        for dep in target.dependencies:
            if dep in self.symbols and dep not in visited:
                visited.add(dep)
                queue.append(self.symbols[dep])

        used_tokens = 0
        included: List[str] = []
        chunks: List[str] = []

        for sym in queue:
            # If full content fits within budget, include it
            if used_tokens + sym.estimated_tokens <= token_budget:
                header = f"### File: {sym.file_path} (Lines {sym.line_start}-{sym.line_end}) [{sym.symbol_type}: {sym.name}]"
                chunks.append(f"{header}\n{sym.content}\n")
                used_tokens += sym.estimated_tokens
                included.append(sym.name)
            else:
                # Fallback to signature + docstring if full content exceeds budget
                summary = f"### File: {sym.file_path} [{sym.symbol_type} signature: {sym.name}]\n{sym.signature}\nDoc: {sym.docstring}\n"
                summary_tokens = max(1, len(summary) // 4)
                if used_tokens + summary_tokens <= token_budget:
                    chunks.append(summary)
                    used_tokens += summary_tokens
                    included.append(f"{sym.name}:sig")
                else:
                    break

        return ContextManifest(
            target_symbol=target_name,
            budget_tokens=token_budget,
            used_tokens=used_tokens,
            included_symbols=included,
            context_text="\n".join(chunks)
        )
