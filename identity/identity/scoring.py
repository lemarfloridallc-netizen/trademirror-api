"""
Mirror Identity Engine - Scoring

This file calculates the first behavioral scores for the
Mirror Identity Framework (MIF).

All scores return a number from 0 to 100.
"""

from typing import Dict, Any


def clamp_score(value: float) -> float:
    """Keep every score between 0 and 100."""
    return max(0, min(100, round(value, 2)))


def calculate_statistical_edge_score(metrics: Dict[str, Any]) -> float:
    """
    Measures whether the trader has a measurable statistical edge.

    Inputs expected:
    - win_rate
    - profit_factor
    - total_trades
    """

    win_rate = float(metrics.get("win_rate", 0) or 0)
    profit_factor = float(metrics.get("profit_factor", 0) or 0)
    total_trades = int(metrics.get("total_trades", 0) or 0)

    win_rate_score = min(win_rate, 100)

    profit_factor_score = min(profit_factor / 2.0 * 100, 100)

    if total_trades >= 100:
        sample_score = 100
    elif total_trades >= 50:
        sample_score = 80
    elif total_trades >= 20:
        sample_score = 60
    elif total_trades >= 10:
        sample_score = 40
    else:
        sample_score = 20

    score = (
        win_rate_score * 0.40
        + profit_factor_score * 0.40
        + sample_score * 0.20
    )

    return clamp_score(score)


def calculate_risk_management_score(metrics: Dict[str, Any]) -> float:
    """
    Measures how well the trader protects capital.

    Inputs expected:
    - gross_profit
    - gross_loss
    - net_pnl
    """

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
    """
    Measures whether the trader produces stable results.

    Inputs expected:
    - win_rate
    - profit_factor
    - total_trades
    - net_pnl
    """

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


def calculate_identity_scores(metrics: Dict[str, Any]) -> Dict[str, float]:
    """
    Main scoring function for MIF v1.

    Some dimensions use placeholder logic for now.
    They will be improved later when trade-level data is available.
    """

    statistical_edge = calculate_statistical_edge_score(metrics)
    risk_management = calculate_risk_management_score(metrics)
    consistency = calculate_consistency_score(metrics)

    return {
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
