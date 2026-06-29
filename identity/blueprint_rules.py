"""
Mirror Blueprint Generator - Blueprint Rules

Transforms trader metrics into personalized blueprint recommendations.

This module does NOT identify the trader.
It PERSONALIZES the blueprint using historical evidence.
"""

from typing import Dict, Any


def generate_personalized_rules(metrics: Dict[str, Any]) -> Dict[str, Any]:

    best_asset = metrics.get("best_asset", "Unknown")
    best_profit_factor = metrics.get("profit_factor", 0)
    total_trades = metrics.get("total_trades", 0)

    rules = {

        "recommended_asset": best_asset,

        "recommended_max_trades":
            1 if total_trades < 20 else 2,

        "recommended_profit_factor":
            round(best_profit_factor, 2),

        "recommended_daily_focus":
            "Quality over quantity.",

        "recommended_session":
            "Use historical best trading window.",

        "recommended_execution":
            "Repeat only your highest probability setups.",

        "recommended_psychology":
            "Protect your statistical edge before seeking more trades."

    }

    return rules
