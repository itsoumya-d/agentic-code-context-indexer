# Agentic Code Context Indexer

AST-aware symbol dependency graph and token-budgeted context assembler designed to give AI coding agents precise repository context.

## Capabilities
- AST symbol extraction (classes, functions, methods, docstrings).
- Dependency call-graph resolution across modular source files.
- Greedy token-budget packing and relevance ranking for agent prompt harnesses.
- Eliminates context window bloat and truncation during multi-file agentic refactoring.

## Testing
```bash
pytest -v
```
