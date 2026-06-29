from identity.signal_detector import detect_behavioral_signals
def calculate_statistical_edge_score(metrics):
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
def calculate_signal_adjustments(metrics):
    """
    Convert detected behavioral signals into score adjustments.

    v1 uses simple adjustments.
    Future versions will weight signals by frequency and confidence.
    """

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

    if "BS003" in signals:
        adjustments["discipline_score"] += 5
        adjustments["risk_management_score"] += 5
        adjustments["psychology_score"] += 3

    if "BS006" in signals:
        adjustments["execution_score"] += 5
        adjustments["statistical_edge_score"] += 5
        adjustments["consistency_score"] += 3

    if "BS007" in signals:
        adjustments["discipline_score"] -= 8
        adjustments["psychology_score"] -= 6
        adjustments["risk_management_score"] -= 5

    if "BS008" in signals:
        adjustments["selection_score"] += 5
        adjustments["consistency_score"] += 3
        adjustments["statistical_edge_score"] += 3

    if "BS009" in signals:
        adjustments["risk_management_score"] -= 10
        adjustments["psychology_score"] -= 8
        adjustments["discipline_score"] -= 5

    if "BS010" in signals:
        adjustments["risk_management_score"] += 5
        adjustments["discipline_score"] += 3
        adjustments["consistency_score"] += 3

    return adjustments
