"""
Mirror Identity Engine - Matcher

Compares a trader's MIF score vector against official trading profiles.

This module answers:
"Which trader identity profile is most similar to this trader?"
"""

from typing import Dict, Any, List
from math import sqrt

from identity.profiles import TRADING_PROFILES


MIF_SCORE_KEYS = [
    "patience_score",
    "discipline_score",
    "risk_management_score",
    "selection_score",
    "consistency_score",
    "adaptability_score",
    "execution_score",
    "psychology_score",
    "statistical_edge_score",
    "evolution_score",
]


def calculate_distance(scores: Dict[str, float], targets: Dict[str, float]) -> float:
    """
    Calculate Euclidean distance between trader scores and profile targets.
    Lower distance means closer match.
    """

    squared_differences = []

    for key in MIF_SCORE_KEYS:
        score_value = float(scores.get(key, 0) or 0)
        target_value = float(targets.get(key, 0) or 0)
        squared_differences.append((score_value - target_value) ** 2)

    return sqrt(sum(squared_differences))


def distance_to_match_percentage(distance: float) -> float:
    """
    Convert distance to an approximate match percentage.

    Max theoretical distance across 10 dimensions is about 316.23.
    """

    max_distance = sqrt(10 * (100 ** 2))
    match = 100 * (1 - (distance / max_distance))

    return round(max(0, min(100, match)), 2)


def match_identity_profiles(scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Rank all trading profiles by similarity to trader scores.
    """

    matches = []

    for profile_key, profile in TRADING_PROFILES.items():
        targets = profile.get("targets", {})
        distance = calculate_distance(scores, targets)
        match_percentage = distance_to_match_percentage(distance)

        matches.append({
            "profile_key": profile_key,
            "identity_code": profile.get("identity_code"),
            "identity_name": profile.get("identity_name"),
            "identity_description": profile.get("identity_description"),
            "match_percentage": match_percentage,
            "distance": round(distance, 2),
        })

    matches.sort(key=lambda item: item["match_percentage"], reverse=True)

    return matches


def get_best_identity_match(scores: Dict[str, float]) -> Dict[str, Any]:
    """
    Return the best matching identity profile.
    """

    matches = match_identity_profiles(scores)

    if not matches:
        return {
            "profile_key": "UNKNOWN",
            "identity_code": None,
            "identity_name": "Developing Trader",
            "identity_description": (
                "Tu identidad operativa todavía está en formación. "
                "El sistema necesita más datos para detectar tu patrón dominante."
            ),
            "match_percentage": 0,
            "distance": None,
        }

    return matches[0]
