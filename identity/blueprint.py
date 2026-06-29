"""
Mirror Blueprint Generator - Blueprint

Generates a personalized trading blueprint from the trader identity,
scores, behavioral signals, and metrics.

The blueprint answers:
"How should this trader operate next?"
"""

from typing import Dict, Any


def generate_trading_blueprint(identity_payload: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    identity_name = identity_payload.get("identity_name", "Developing Trader")
    best_asset = metrics.get("best_asset", "Not enough data")

    edge_score = float(identity_payload.get("edge_score", 0) or 0)
    confidence_score = float(identity_payload.get("confidence_score", 0) or 0)
    behavioral_signals = identity_payload.get("behavioral_signals", [])

    if identity_name == "Precision Trader":
        blueprint = {
            "blueprint_version": 1,
            "primary_asset": best_asset,
            "preferred_market_condition": "Clear structure, controlled volatility, confirmed direction",
            "ideal_entry_model": "Wait for confirmation before entry. Avoid chasing late moves.",
            "ideal_exit_model": "Respect planned risk and allow qualified winners to develop.",
            "ideal_tp": 20,
            "ideal_sl": 30,
            "max_trades_per_day": 2,
            "max_daily_risk": 2,
            "preferred_start_time": "Market open + confirmation window",
            "preferred_end_time": "Before performance deterioration",
            "execution_rules": (
                "Trade only confirmed setups. Wait for structure. "
                "Prioritize quality over frequency."
            ),
            "forbidden_rules": (
                "Do not chase price. Do not increase risk after a loss. "
                "Do not trade outside your plan."
            ),
            "daily_checklist": (
                "1. Confirm market direction. "
                "2. Confirm setup quality. "
                "3. Define risk before entry. "
                "4. Limit number of trades. "
                "5. Stop after emotional deterioration."
            ),
            "weekly_focus": "Protect execution quality and reduce unnecessary trades.",
            "coach_message": (
                "Tu ventaja aparece cuando proteges tu estándar. "
                "No necesitas operar más; necesitas operar mejor."
            ),
        }
    else:
        blueprint = {
            "blueprint_version": 1,
            "primary_asset": best_asset,
            "preferred_market_condition": "Only trade clear, measurable setups",
            "ideal_entry_model": "Wait for confirmation and avoid impulsive entries.",
            "ideal_exit_model": "Use predefined risk and avoid emotional exits.",
            "ideal_tp": 15,
            "ideal_sl": 30,
            "max_trades_per_day": 1,
            "max_daily_risk": 1,
            "preferred_start_time": "Best historical window",
            "preferred_end_time": "Stop after first loss or loss of focus",
            "execution_rules": "Trade less, document more, and protect capital.",
            "forbidden_rules": "No revenge trading. No oversized trades. No random setups.",
            "daily_checklist": (
                "1. Confirm setup. "
                "2. Define risk. "
                "3. Take only one qualified trade. "
                "4. Review result."
            ),
            "weekly_focus": "Build consistency before increasing activity.",
            "coach_message": (
                "Tu identidad todavía está en formación. "
                "La prioridad es crear evidencia limpia y repetible."
            ),
        }

    blueprint["confidence_score"] = confidence_score
    blueprint["edge_score"] = edge_score
    blueprint["source_identity"] = identity_name
    blueprint["behavioral_signals_used"] = behavioral_signals

    return blueprint
