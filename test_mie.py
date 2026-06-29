"""
Mirror Identity Engine - Integration Test

Temporary local test.
This file is NOT used by the API.
"""

from pprint import pprint

from identity.engine import build_trading_identity


sample_metrics = {
    "win_rate": 64.71,
    "profit_factor": 1.34,
    "total_trades": 17,
    "gross_profit": 1816.86,
    "gross_loss": 1359.58,
    "net_pnl": 457.28,
}

result = build_trading_identity(sample_metrics)

print("\n==============================")
print(" MIRROR IDENTITY ENGINE TEST")
print("==============================\n")

pprint(result)

print("\n========== END TEST ==========\n")
