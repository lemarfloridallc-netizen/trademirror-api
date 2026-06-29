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
