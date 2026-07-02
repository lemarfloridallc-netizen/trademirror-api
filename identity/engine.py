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


def generate_mirror_insight(
    identity_payload: Dict[str, Any],
    metrics: Dict[str, Any]
) -> Dict[str, Any]:
    identity_name = identity_payload.get("identity_name", "Trader")
    edge_score = float(identity_payload.get("edge_score", 0) or 0)
    confidence_score = float(identity_payload.get("confidence_score", 0) or 0)
    profit_factor = float(metrics.get("profit_factor", 0) or 0)
    win_rate = float(metrics.get("win_rate", 0) or 0)
    total_trades = int(metrics.get("total_trades", 0) or 0)

    if edge_score >= 80:
        headline = "Your trading identity is becoming a real edge."
    elif edge_score >= 60:
        headline = "Your edge is forming, but consistency still matters."
    else:
        headline = "Your edge needs more structure before it can compound."

    if profit_factor >= 1.5:
        main_observation = (
            f"As a {identity_name}, your recent performance shows a positive "
            "statistical structure. Your strongest opportunity is to keep repeating "
            "the behaviors that produced your best trades."
        )
    elif profit_factor >= 1.0:
        main_observation = (
            f"As a {identity_name}, you are close to building a sustainable edge. "
            "Your next level depends on improving trade selection, discipline, "
            "and emotional consistency."
        )
    else:
        main_observation = (
            f"As a {identity_name}, your current data suggests that your process "
            "needs more protection. The priority is not more trades. The priority "
            "is better decisions."
        )

    if win_rate < 45:
        risk_warning = (
            "Your win rate suggests that selectivity may be one of your main areas "
            "to improve. Avoid forcing trades when the setup is not clear."
        )
    elif profit_factor < 1:
        risk_warning = (
            "Your profit factor shows that losses are still outweighing winners. "
            "Protecting risk must remain your first priority."
        )
    else:
        risk_warning = (
            "Your current risk profile is improving. Continue protecting your best "
            "setup and avoid overtrading after emotional moments."
        )

    if total_trades < 20:
        today_focus = (
            "Keep collecting clean data. Your sample size is still small, so focus "
            "on discipline and consistency before judging your edge."
        )
    elif confidence_score < 60:
        today_focus = (
            "Trade less, observe more, and protect your process. One clean trade is "
            "more valuable than several impulsive entries."
        )
    else:
        today_focus = (
            "Protect your patience today. Your best growth comes from repeating the "
            "behaviors that support your edge."
        )

    return {
        "headline": headline,
        "main_observation": main_observation,
        "risk_warning": risk_warning,
        "today_focus": today_focus,
    }


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

    mirror_insight = generate_mirror_insight(
        identity_payload,
        metrics
    )

    identity_payload["blueprint"] = blueprint
    identity_payload["mirror_insight"] = mirror_insight

    return identity_payload
