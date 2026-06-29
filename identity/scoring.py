"""
Mirror Identity Engine - Scoring

Calculates behavioral dimension scores for the
Mirror Identity Framework (MIF).

All scores return a number from 0 to 100.
"""

from typing import Dict, Any

from identity.signal_detector import detect_behavioral_signals
from identity.signal_matrix import SIGNAL_MATRIX


def clamp_score(value: float) -> float:
    """Keep every score between 0 and 100."""
    return max(0, min(100, round(value, 2)))


def calculate_statistical_edge_score(metrics: Dict[str, Any]) -> float:
    win_rate = float(metrics.get("win_rate", 0) or 0)
    profit_factor = float(metrics.get("profit_factor", 0) or 0)
    total_trades = int(metrics.get("total_trades", 0) or 0)

    win_rate_score = min(win_rate, 100)
    profit_factor_score = min((profit_factor / 2.0) * 100, 100)

    if total_trades >= 100:
        sample_size_score = 100
    elif total_trades >= 50:
        sample_size_score = 80
    elif total_trades >= 20:
        sample_size_score = 60
    elif total_trades >= 10:
        sample_size_score = 40
    else:
        sample_size_score = 20

    score = (
        win_rate_score * 0.40
        + profit_factor_score * 0.40
        + sample_size_score * 0.20
    )

    return clamp_score(score)


def calculate_risk_management_score(metrics: Dict[str, Any]) -> float:
    gross_profit = float(metrics.get("gross_profit", 0) or 0)
    gross_loss = abs(float(metrics.get("gross_loss", 0) or 0))
    net_pnl = float(metrics.get("net_pnl", 0) or 0)

    if gross_loss == 0:
        return 100 if gross_profit > 0 else 50

    loss_ratio = gross_loss / max(gross_profit, 1)

    if net_pnl <= 0:
        base = 35
    elif loss_ratio <= 0.35:
        base = 95
    elif loss_ratio <= 0.50:
        base = 85
    elif loss_ratio <= 0.75:
        base = 70
    elif loss_ratio <= 1.00:
        base = 55
    else:
        base = 40

    return clamp_score(base)


def calculate_consistency_score(metrics: Dict[str, Any]) -> float:
    win_rate = float(metrics.get("win_rate", 0) or 0)
    profit_factor = float(metrics.get("profit_factor", 0) or 0)
    total_trades = int(metrics.get("total_trades", 0) or 0)
    net_pnl = float(metrics.get("net_pnl", 0) or 0)

    score = 50

    if net_pnl > 0:
        score += 15

    if win_rate >= 60:
        score += 15
    elif win_rate >= 50:
        score += 8

    if profit_factor >= 1.5:
        score += 15
    elif profit_factor >= 1.2:
        score += 8

    if total_trades >= 50:
        score += 10
    elif total_trades >= 20:
        score += 5

    return clamp_score(score)


def calculate_signal_adjustments(metrics: Dict[str, Any]) -> Dict[str, float]:
    signals = detect_behavioral_signals(metrics)

    adjustments = {
        "patience_score": 0,
        "discipline_score": 0,
        "risk_management_score": 0,
        "selection_score": 0,
        "consistency_score": 0,
        "adaptability_score": 0,
        "execution_score": 0,
        "psychology_score": 0,
        "statistical_edge_score": 0,
        "evolution_score": 0,
    }

    for signal_code in signals:
        signal_weights = SIGNAL_MATRIX.get(signal_code, {})

        for dimension, impact in signal_weights.items():
            adjustments[dimension] += impact

    return adjustments


def calculate_identity_scores(metrics: Dict[str, Any]) -> Dict[str, float]:
    statistical_edge = calculate_statistical_edge_score(metrics)
    risk_management = calculate_risk_management_score(metrics)
    consistency = calculate_consistency_score(metrics)

    base_scores = {
        "statistical_edge_score": statistical_edge,
        "risk_management_score": risk_management,
        "consistency_score": consistency,

        # Temporary v1 estimates until trade-level data is added
        "discipline_score": consistency,
        "execution_score": consistency,
        "patience_score": consistency,
        "selection_score": statistical_edge,
        "psychology_score": risk_management,
        "adaptability_score": 50,
        "evolution_score": 50,
    }

    adjustments = calculate_signal_adjustments(metrics)

    final_scores = {}

    for key, value in base_scores.items():
        final_scores[key] = clamp_score(value + adjustments.get(key, 0))

    return final_scores
