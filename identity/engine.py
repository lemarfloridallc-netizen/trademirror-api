"""
Mirror Identity Engine - Engine

Main orchestration layer for the Mirror Identity Engine (MIE).

Responsibilities:
- Receive trading metrics
- Detect behavioral signals
- Calculate signal confidence
- Calculate dimension scores
- Match trader against official identity profiles
- Calculate Edge Score
- Calculate Confidence Score

This module does not modify the public API by itself.
main.py will call this later.
"""

from typing import Dict, Any

from identity.dimensions import DIMENSION_WEIGHTS
from identity.signal_detector import detect_behavioral_signals
from identity.confidence import calculate_detected_signal_confidences
from identity.scoring import calculate_identity_scores, clamp_score
from identity.matcher import match_identity_profiles, get_best_identity_match


def calculate_edge_score(scores: Dict[str, float]) -> float:
    total = 0.0

    for dimension, weight in DIMENSION_WEIGHTS.items():
        total += float(scores.get(dimension, 0) or 0) * weight

    return clamp_score(total)


def calculate_confidence_score(metrics: Dict[str, Any]) -> float:
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


def build_trading_identity(metrics: Dict[str, Any]) -> Dict[str, Any]:
    signals = detect_behavioral_signals(metrics)
    signal_confidences = calculate_detected_signal_confidences(signals, metrics)
    scores = calculate_identity_scores(metrics)

    identity_matches = match_identity_profiles(scores)
    best_match = get_best_identity_match(scores)

    edge_score = calculate_edge_score(scores)
    confidence_score = calculate_confidence_score(metrics)

    return {
        "identity_name": best_match["identity_name"],
        "identity_code": best_match["identity_code"],
        "identity_description": best_match["identity_description"],
        "identity_match_percentage": best_match["match_percentage"],
        "identity_distance": best_match["distance"],

        "edge_score": edge_score,
        "confidence_score": confidence_score,
        "identity_version": 2,
        "reports_analyzed": 1,

        "behavioral_signals": signals,
        "signal_confidences": signal_confidences,
        "identity_matches": identity_matches[:3],

        **scores,
    }
