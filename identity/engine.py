"""
Mirror Identity Engine - Engine

Main orchestration layer for the Mirror Identity Engine (MIE).
"""

from typing import Dict, Any

from identity.dimensions import DIMENSION_WEIGHTS
from identity.signal_detector import detect_behavioral_signals
from identity.confidence import calculate_detected_signal_confidences
from identity.scoring import calculate_identity_scores, clamp_score
from identity.matcher import match_identity_profiles, get_best_identity_match
from identity.blueprint import generate_trading_blueprint


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

    # Detect behavioral signals
    signals = detect_behavioral_signals(metrics)

    # Confidence per signal
    signal_confidences = calculate_detected_signal_confidences(
        signals,
        metrics
    )

    # Dimension scores
    scores = calculate_identity_scores(metrics)

    # Match against official identities
    identity_matches = match_identity_profiles(scores)
    best_match = get_best_identity_match(scores)

    edge_score = calculate_edge_score(scores)
    confidence_score = calculate_confidence_score(metrics)

    identity_payload = {
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

    blueprint = generate_trading_blueprint(
        identity_payload,
        metrics
    )

    identity_payload["blueprint"] = blueprint

    return identity_payload
