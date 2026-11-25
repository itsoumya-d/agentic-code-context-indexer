from src.indexer.models import SymbolNode

def test_models_scaffold():
    node = SymbolNode(
        name="calculate_payout",
        symbol_type="function",
        file_path="src/payout.py",
        line_start=10,
        line_end=25,
        signature="def calculate_payout(amount: float) -> float:"
    )
    assert node.name == "calculate_payout"
    assert node.symbol_type == "function"
