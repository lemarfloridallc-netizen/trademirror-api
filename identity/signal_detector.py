"""
Mirror Identity Engine - Signal Detector

This file detects behavioral signals from trading metrics.

v1 uses aggregated report metrics.
Future versions will use trade-level data.
"""

from typing import Dict, Any, List


def detect_behavioral_signals(metrics: Dict[str, Any]) -> List[str]:
    """
    Detect behavioral signal codes from report metrics.

    Returns:
        List of Behavioral Signal codes.
    """

    signals = []

    win_rate = float(metrics.get("win_rate", 0) or 0)
    profit_factor = float(metrics.get("profit_factor", 0) or 0)
    total_trades = int(metrics.get("total_trades", 0) or 0)
    gross_profit = float(metrics.get("gross_profit", 0) or 0)
    gross_loss = abs(float(metrics.get("gross_loss", 0) or 0))
    net_pnl = float(metrics.get("net_pnl", 0) or 0)

    # BS006 — Lets Winners Run
    if profit_factor >= 1.5 and net_pnl > 0:
        signals.append("BS006")

    # BS007 — Overtrades
    if total_trades > 50 and profit_factor < 1.2:
        signals.append("BS007")

    # BS010 — Consistent Position Size
    if total_trades >= 20 and gross_loss > 0 and gross_profit > 0:
        loss_ratio = gross_loss / gross_profit

        if 0.35 <= loss_ratio <= 0.85:
            signals.append("BS010")

    # BS003 — Respects Stop Loss
    if gross_loss > 0 and gross_profit > 0:
        loss_ratio = gross_loss / gross_profit

        if loss_ratio <= 0.75 and net_pnl > 0:
            signals.append("BS003")

    # BS009 — Increases Risk After Loss
    if net_pnl < 0 and gross_loss > gross_profit:
        signals.append("BS009")

    # BS008 — Trades in Ideal Session
    # Placeholder until time-based trade data is available.
    if win_rate >= 60 and profit_factor >= 1.2:
        signals.append("BS008")

    return signals
