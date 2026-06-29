from identity.signal_detector import detect_behavioral_signals
from identity.scoring import calculate_identity_scores
from identity.engine import build_trading_identity

sample_metrics = {
    "win_rate": 64.71,
    "profit_factor": 1.34,
    "total_trades": 17,
    "gross_profit": 1816.86,
    "gross_loss": 1359.58,
    "net_pnl": 457.28,
}

signals = detect_behavioral_signals(sample_metrics)
scores = calculate_identity_scores(sample_metrics)
identity = build_trading_identity(sample_metrics)

print("SIGNALS:")
print(signals)

print("\nSCORES:")
print(scores)

print("\nIDENTITY:")
print(identity)
