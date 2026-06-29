"""
Mirror Identity Engine - Confidence

Calculates confidence levels for detected behavioral signals.

Confidence answers:
"How reliable is this detected signal based on available evidence?"

All confidence values return a number from 0 to 100.
"""

from typing import Dict, Any, List


def clamp_confidence(value: float) -> float:
    """Keep every confidence value between 0 and 100."""
    return max(0, min(100, round(value, 2)))


def calculate_sample_confidence(total_trades: int) -> float:
    """
    Estimate confidence based on sample size.
    """

    if total_trades >= 200:
        return 95
    if total_trades >= 100:
        return 85
    if total_trades >= 50:
        return 70
    if total_trades >= 20:
        return 55
    if total_trades >= 10:
        return 35

    return 15


def calculate_signal_confidence(
    signal_code: str,
    metrics: Dict[str, Any],
) -> float:
    """
    Calculate confidence for one behavioral signal.

    v1 uses sample size and signal-specific confidence limits.
    Future versions will use trade-level evidence.
    """

    total_trades = int(metrics.get("total_trades", 0) or 0)
    sample_confidence = calculate_sample_confidence(total_trades)

    signal_caps = {
        "BS001": 45,
        "BS002": 35,
        "BS003": 65,
        "BS004": 45,
        "BS005": 50,
        "BS006": 60,
        "BS007": 60,
        "BS008": 45,
        "BS009": 40,
        "BS010": 60,
    }

    max_v1_confidence = signal_caps.get(signal_code, 40)

    return clamp_confidence(min(sample_confidence, max_v1_confidence))


def calculate_detected_signal_confidences(
    signals: List[str],
    metrics: Dict[str, Any],
) -> Dict[str, float]:
    """
    Calculate confidence for all detected signals.
    """

    return {
        signal_code: calculate_signal_confidence(signal_code, metrics)
        for signal_code in signals
    }
