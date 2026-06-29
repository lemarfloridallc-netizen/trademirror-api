"""
Mirror Identity Engine - Engine

Main orchestration layer for the Mirror Identity Engine (MIE).

Responsibilities:
- Receive trading metrics
- Detect behavioral signals
- Calculate signal confidence
- Calculate dimension scores
- Calculate Edge Score
- Calculate Confidence Score
- Classify preliminary trader identity

This module does not modify the public API by itself.
main.py will call this later.
"""

from typing import Dict, Any

from identity.dimensions import DIMENSION_WEIGHTS
from identity.signal_detector import detect_behavioral_signals
from identity.confidence import calculate_detected_signal_confidences
from identity.scoring import calculate_identity_scores, clamp_score


def calculate_edge_score(scores: Dict[str, float]) -> float:
    """
    Calculate weighted Edge Score using official MIF dimension weights.
    """

    total = 0.0

    for dimension, weight in DIMENSION_WEIGHTS.items():
        total += float(scores.get(dimension, 0) or 0) * weight

    return clamp_score(total)


def calculate_confidence_score(metrics: Dict[str, Any]) -> float:
    """
    Estimate general diagnosis confidence.

    v1 uses total sample size.
    Future versions will include:
    - number of reports
    - stability across periods
    - quality of trade-level data
    """

    total_trades = int(metrics.get("total_trades", 0) or 0)

    if total_trades >= 200:
        confidence = 95
    elif total_trades >= 100:
        confidence = 85
    elif total_trades >= 50:
        confidence = 70
    elif total_trades >= 20:
        confidence = 55
    elif total_trades >= 10:
        confidence = 35
    else:
        confidence = 15

    return clamp_score(confidence)


def classify_identity(scores: Dict[str, float]) -> Dict[str, str]:
    """
    Preliminary MIE v1 identity classifier.

    This is intentionally conservative.
    Later versions will compare the score vector against
    TradingIdentityProfile archetype targets.
    """

    discipline = scores.get("discipline_score", 0)
    consistency = scores.get("consistency_score", 0)
    statistical_edge = scores.get("statistical_edge_score", 0)
    risk = scores.get("risk_management_score", 0)
    selection = scores.get("selection_score", 0)

    if discipline >= 80 and consistency >= 75 and risk >= 70:
        return {
            "identity_name": "Precision Trader",
            "identity_description": (
                "Tu mejor rendimiento aparece cuando esperas confirmaciones, "
                "proteges el capital y repites patrones de alta calidad."
            ),
        }

    if statistical_edge >= 75 and selection >= 75:
        return {
            "identity_name": "Momentum Builder",
            "identity_description": (
                "Tu ventaja aparece cuando encuentras activos con fuerza clara "
                "y concentras tu rendimiento en oportunidades superiores."
            ),
        }

    if risk >= 80 and statistical_edge < 70:
        return {
            "identity_name": "Capital Guardian",
            "identity_description": (
                "Tu fortaleza principal está en proteger el capital, aunque tu "
                "ventaja estadística todavía necesita mayor desarrollo."
            ),
        }

    return {
        "identity_name": "Developing Trader",
        "identity_description": (
            "Tu identidad operativa todavía está en formación. El sistema necesita "
            "más datos para detectar con alta confianza tu patrón dominante."
        ),
    }


def build_trading_identity(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main MIE v1 function.

    Input:
        metrics dictionary from the existing CSV analyzer.

    Output:
        Structured identity payload that Bubble can later store
        in TradingIdentity.
    """

    signals = detect_behavioral_signals(metrics)
    signal_confidences = calculate_detected_signal_confidences(signals, metrics)
    scores = calculate_identity_scores(metrics)

    edge_score = calculate_edge_score(scores)
    confidence_score = calculate_confidence_score(metrics)
    identity = classify_identity(scores)

    return {
        "identity_name": identity["identity_name"],
        "identity_description": identity["identity_description"],
        "edge_score": edge_score,
        "confidence_score": confidence_score,
        "identity_version": 1,
        "reports_analyzed": 1,

        "behavioral_signals": signals,
        "signal_confidences": signal_confidences,

        **scores,
    }
