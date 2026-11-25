import pytest
from src.indexer.parser import CodeASTIndexer

SAMPLE_CODE = """
def validate_token(token: str) -> bool:
    \"\"\"Checks token validity.\"\"\"
    return len(token) > 10

def sanitize_payload(payload: dict) -> dict:
    \"\"\"Strips dangerous fields.\"\"\"
    return {k: v for k, v in payload.items() if k != "secret"}

class AgentContextManager:
    \"\"\"Manages execution context for coding agents.\"\"\"
    def __init__(self, token: str):
        self.is_valid = validate_token(token)

    def process(self, data: dict):
        clean = sanitize_payload(data)
        return clean
"""

def test_ast_symbol_extraction():
    indexer = CodeASTIndexer()
    symbols = indexer.parse_source(SAMPLE_CODE, "src/agent.py")
    assert len(symbols) == 3
    names = {s.name for s in symbols}
    assert "validate_token" in names
    assert "sanitize_payload" in names
    assert "AgentContextManager" in names

def test_dependency_call_extraction():
    indexer = CodeASTIndexer()
    indexer.parse_source(SAMPLE_CODE, "src/agent.py")
    mgr = indexer.symbols["AgentContextManager"]
    assert "validate_token" in mgr.dependencies
    assert "sanitize_payload" in mgr.dependencies

def test_token_budget_context_assembly():
    indexer = CodeASTIndexer()
    indexer.parse_source(SAMPLE_CODE, "src/agent.py")

    manifest = indexer.assemble_context("AgentContextManager", token_budget=500)
    assert manifest.target_symbol == "AgentContextManager"
    assert "AgentContextManager" in manifest.included_symbols
    assert "validate_token" in manifest.included_symbols
    assert "sanitize_payload" in manifest.included_symbols
    assert manifest.used_tokens <= 500

def test_token_budget_pruning_under_tight_cap():
    indexer = CodeASTIndexer()
    indexer.parse_source(SAMPLE_CODE, "src/agent.py")

    # Tight budget: only target can fit
    manifest = indexer.assemble_context("AgentContextManager", token_budget=40)
    assert manifest.used_tokens <= 40
    assert len(manifest.included_symbols) >= 1
