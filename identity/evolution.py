# identity/evolution.py

from typing import Any, Dict, List


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return round(max(minimum, min(value, maximum)), 2)


def get_pnl(trade: Dict[str, Any]) -> float:
    return safe_float(
        trade.get("pnl")
        or trade.get("realized_pnl")
        or trade.get("net_pnl")
        or trade.get("profit")
        or 0
    )


def get_asset(trade: Dict[str, Any]) -> str:
    return (
        trade.get("asset")
        or trade.get("asset_base")
        or trade.get("ticker")
        or trade.get("symbol")
        or "UNKNOWN"
    )


def calculate_profit_factor(gross_profit: float, gross_loss: float) -> float:
    gross_profit = safe_float(gross_profit)
    gross_loss = abs(safe_float(gross_loss))

    if gross_loss == 0:
        return 999.0 if gross_profit > 0 else 0.0

    return round(gross_profit / gross_loss, 2)


def split_trades_by_time(trades: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    if len(trades) < 2:
        return {"previous_period": [], "current_period": trades}

    midpoint = len(trades) // 2

    return {
        "previous_period": trades[:midpoint],
        "current_period": trades[midpoint:],
    }


def calculate_overtrading_score(trades: List[Dict[str, Any]]) -> float:
    total = len(trades)

    if total <= 5:
        return 10.0
    if total <= 10:
        return 20.0
    if total <= 20:
        return 35.0
    if total <= 40:
        return 55.0
    if total <= 75:
        return 75.0

    return 100.0


def summarize_period(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_trades = len(trades)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "net_pnl": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "profit_factor": 0.0,
            "capital_leak": 0.0,
            "best_asset": None,
            "worst_asset": None,
            "asset_summary": {},
            "overtrading_score": 0.0,
            "post_loss_recovery_score": 0.0,
            "average_winner": 0.0,
            "average_loser": 0.0,
            "payoff_ratio": 0.0,
            "largest_loss": 0.0,
            "largest_win": 0.0,
            "max_losing_streak": 0,
        }

    pnls = [get_pnl(trade) for trade in trades]

    winners = [pnl for pnl in pnls if pnl > 0]
    losers = [pnl for pnl in pnls if pnl < 0]

    gross_profit = sum(winners)
    gross_loss = abs(sum(losers))
    net_pnl = sum(pnls)

    win_rate = round((len(winners) / total_trades) * 100, 2)
    profit_factor = calculate_profit_factor(gross_profit, gross_loss)

    average_winner = round(gross_profit / len(winners), 2) if winners else 0.0
    average_loser = round(-gross_loss / len(losers), 2) if losers else 0.0
    payoff_ratio = round(average_winner / abs(average_loser), 2) if average_loser else 0.0

    asset_summary: Dict[str, Dict[str, Any]] = {}

    for trade in trades:
        asset = get_asset(trade)
        pnl = get_pnl(trade)

        if asset not in asset_summary:
            asset_summary[asset] = {
                "trades": 0,
                "net_pnl": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "profit_factor": 0.0,
            }

        asset_summary[asset]["trades"] += 1
        asset_summary[asset]["net_pnl"] += pnl

        if pnl > 0:
            asset_summary[asset]["gross_profit"] += pnl
        elif pnl < 0:
            asset_summary[asset]["gross_loss"] += pnl

    for asset, data in asset_summary.items():
        data["net_pnl"] = round(data["net_pnl"], 2)
        data["gross_profit"] = round(data["gross_profit"], 2)
        data["gross_loss"] = round(data["gross_loss"], 2)
        data["profit_factor"] = calculate_profit_factor(
            data["gross_profit"],
            data["gross_loss"],
        )

    best_asset = max(asset_summary.items(), key=lambda x: x[1]["net_pnl"])[0] if asset_summary else None
    worst_asset = min(asset_summary.items(), key=lambda x: x[1]["net_pnl"])[0] if asset_summary else None

    max_losing_streak = 0
    current_losing_streak = 0

    for pnl in pnls:
        if pnl < 0:
            current_losing_streak += 1
            max_losing_streak = max(max_losing_streak, current_losing_streak)
        else:
            current_losing_streak = 0

    previous_trade_was_loss = False
    post_loss_trades = 0
    post_loss_wins = 0

    for pnl in pnls:
        if previous_trade_was_loss:
            post_loss_trades += 1
            if pnl > 0:
                post_loss_wins += 1

        previous_trade_was_loss = pnl < 0

    post_loss_recovery_score = (
        round((post_loss_wins / post_loss_trades) * 100, 2)
        if post_loss_trades > 0
        else 0.0
    )

    return {
        "total_trades": total_trades,
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate": win_rate,
        "net_pnl": round(net_pnl, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": profit_factor,
        "capital_leak": round(gross_loss, 2),
        "best_asset": best_asset,
        "worst_asset": worst_asset,
        "asset_summary": asset_summary,
        "overtrading_score": calculate_overtrading_score(trades),
        "post_loss_recovery_score": post_loss_recovery_score,
        "average_winner": average_winner,
        "average_loser": average_loser,
        "payoff_ratio": payoff_ratio,
        "largest_loss": round(min(pnls), 2),
        "largest_win": round(max(pnls), 2),
        "max_losing_streak": max_losing_streak,
    }


def calculate_change(current: float, previous: float) -> Dict[str, Any]:
    current = safe_float(current)
    previous = safe_float(previous)

    absolute_change = round(current - previous, 2)

    if previous == 0:
        percentage_change = 0.0
    else:
        percentage_change = round((absolute_change / abs(previous)) * 100, 2)

    if absolute_change > 0:
        direction = "improved"
    elif absolute_change < 0:
        direction = "declined"
    else:
        direction = "unchanged"

    return {
        "previous": round(previous, 2),
        "current": round(current, 2),
        "absolute_change": absolute_change,
        "percentage_change": percentage_change,
        "direction": direction,
    }


def calculate_negative_change_is_good(current: float, previous: float) -> Dict[str, Any]:
    result = calculate_change(current, previous)

    if result["absolute_change"] < 0:
        result["direction"] = "improved"
    elif result["absolute_change"] > 0:
        result["direction"] = "declined"
    else:
        result["direction"] = "unchanged"

    return result


def score_profit_factor(profit_factor: float) -> float:
    pf = safe_float(profit_factor)

    if pf >= 2.0:
        return 95
    if pf >= 1.5:
        return 82
    if pf >= 1.2:
        return 70
    if pf >= 1.0:
        return 58
    if pf >= 0.75:
        return 42
    if pf >= 0.5:
        return 28

    return 15


def score_win_rate(win_rate: float) -> float:
    wr = safe_float(win_rate)

    if wr >= 70:
        return 90
    if wr >= 60:
        return 78
    if wr >= 50:
        return 65
    if wr >= 40:
        return 50
    if wr >= 30:
        return 35

    return 20


def score_payoff_ratio(payoff_ratio: float) -> float:
    ratio = safe_float(payoff_ratio)

    if ratio >= 2.0:
        return 92
    if ratio >= 1.5:
        return 80
    if ratio >= 1.0:
        return 65
    if ratio >= 0.75:
        return 48
    if ratio >= 0.5:
        return 32

    return 18


def score_recovery(post_loss_recovery_score: float) -> float:
    recovery = safe_float(post_loss_recovery_score)

    if recovery >= 70:
        return 90
    if recovery >= 55:
        return 75
    if recovery >= 45:
        return 60
    if recovery >= 30:
        return 42

    return 25


def score_risk_quality(period: Dict[str, Any]) -> float:
    net_pnl = safe_float(period.get("net_pnl"))
    gross_profit = safe_float(period.get("gross_profit"))
    gross_loss = safe_float(period.get("gross_loss"))
    largest_loss = abs(safe_float(period.get("largest_loss")))
    average_winner = safe_float(period.get("average_winner"))
    max_losing_streak = safe_int(period.get("max_losing_streak"))

    score = 55.0

    if net_pnl > 0:
        score += 18
    else:
        score -= 10

    if gross_profit > 0:
        loss_pressure = gross_loss / gross_profit

        if loss_pressure <= 0.50:
            score += 15
        elif loss_pressure <= 0.85:
            score += 8
        elif loss_pressure <= 1.25:
            score -= 2
        else:
            score -= 12
    elif gross_loss > 0:
        score -= 15

    if average_winner > 0 and largest_loss > average_winner * 2:
        score -= 15
    elif average_winner > 0 and largest_loss <= average_winner:
        score += 8

    if max_losing_streak >= 5:
        score -= 15
    elif max_losing_streak >= 3:
        score -= 8
    elif max_losing_streak <= 1:
        score += 5

    return clamp(score)


def score_growth(changes: Dict[str, Dict[str, Any]]) -> float:
    score = 50.0

    if changes["capital_leak"]["direction"] == "improved":
        score += 18
    elif changes["capital_leak"]["direction"] == "declined":
        score -= 14

    if changes["profit_factor"]["direction"] == "improved":
        score += 16
    elif changes["profit_factor"]["direction"] == "declined":
        score -= 12

    if changes["win_rate"]["direction"] == "improved":
        score += 10
    elif changes["win_rate"]["direction"] == "declined":
        score -= 8

    if changes["post_loss_recovery"]["direction"] == "improved":
        score += 14
    elif changes["post_loss_recovery"]["direction"] == "declined":
        score -= 12

    if changes["overtrading"]["direction"] == "improved":
        score += 12
    elif changes["overtrading"]["direction"] == "declined":
        score -= 8

    return clamp(score)


def score_performance(current_period: Dict[str, Any]) -> float:
    profit_factor_score = score_profit_factor(current_period.get("profit_factor", 0))
    risk_score = score_risk_quality(current_period)
    payoff_score = score_payoff_ratio(current_period.get("payoff_ratio", 0))
    win_rate_score = score_win_rate(current_period.get("win_rate", 0))
    recovery_score = score_recovery(current_period.get("post_loss_recovery_score", 0))

    score = (
        profit_factor_score * 0.28
        + risk_score * 0.27
        + payoff_score * 0.18
        + win_rate_score * 0.15
        + recovery_score * 0.12
    )

    return clamp(score)


def calculate_evolution_score(
    previous_period: Dict[str, Any],
    current_period: Dict[str, Any],
    changes: Dict[str, Dict[str, Any]],
) -> float:
    performance_score = score_performance(current_period)
    growth_score = score_growth(changes)

    # Mirror Confidence:
    # 65% current performance + 35% evolution vs previous period.
    # This keeps the score honest, but does not punish a trader only because
    # the latest period was difficult if there is real behavioral improvement.
    mirror_confidence = (performance_score * 0.65) + (growth_score * 0.35)

    return clamp(mirror_confidence)


def get_evolution_stage(score: float) -> str:
    score = safe_float(score)

    if score >= 85:
        return "elite_evolution"
    if score >= 70:
        return "strong_improvement"
    if score >= 55:
        return "improving"
    if score >= 40:
        return "rebuilding"

    return "critical_decline"


def build_coach_message(
    previous: Dict[str, Any],
    current: Dict[str, Any],
    changes: Dict[str, Dict[str, Any]],
    score: float,
) -> str:
    performance_score = score_performance(current)
    growth_score = score_growth(changes)

    observations = []

    if current.get("profit_factor", 0) >= 1.2:
        observations.append("tu estructura estadística empieza a mostrar ventaja")
    elif current.get("profit_factor", 0) < 1:
        observations.append("tu prioridad es reducir pérdidas grandes antes de buscar más entradas")

    if changes.get("capital_leak", {}).get("direction") == "improved":
        observations.append("estás reduciendo la fuga de capital")
    elif changes.get("capital_leak", {}).get("direction") == "declined":
        observations.append("la fuga de capital aumentó y necesita atención inmediata")

    if current.get("post_loss_recovery_score", 0) < 45:
        observations.append("sigues vulnerable después de una pérdida")
    elif current.get("post_loss_recovery_score", 0) >= 60:
        observations.append("tu recuperación después de pérdidas está mejorando")

    if current.get("payoff_ratio", 0) < 1:
        observations.append("tus pérdidas promedio pesan más que tus ganancias promedio")

    if current.get("worst_asset"):
        observations.append(f"tu mayor debilidad actual está en {current.get('worst_asset')}")

    if score >= 70:
        base = "Estás construyendo una evolución sólida."
    elif score >= 55:
        base = "Tu evolución muestra avance real, aunque todavía requiere más consistencia."
    elif score >= 40:
        base = "Estás en una fase de reconstrucción operativa."
    else:
        base = "Tu evolución muestra señales críticas, pero ya existe información clara para reconstruir tu proceso."

    base += f" Performance Score: {round(performance_score, 1)}. Growth Score: {round(growth_score, 1)}."

    if observations:
        base += " " + ". ".join(observations[:3]) + "."

    return base


def generate_evolution_engine(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not trades:
        return {
            "status": "insufficient_data",
            "evolution_score": 0.0,
            "evolution_stage": "no_data",
            "previous_period": {},
            "current_period": {},
            "changes": {},
            "coach_message": "Necesitamos más operaciones para medir tu evolución como trader.",
        }

    periods = split_trades_by_time(trades)

    previous_period = summarize_period(periods["previous_period"])
    current_period = summarize_period(periods["current_period"])

    changes = {
        "win_rate": calculate_change(
            current_period["win_rate"],
            previous_period["win_rate"],
        ),
        "profit_factor": calculate_change(
            current_period["profit_factor"],
            previous_period["profit_factor"],
        ),
        "capital_leak": calculate_negative_change_is_good(
            current_period["capital_leak"],
            previous_period["capital_leak"],
        ),
        "overtrading": calculate_negative_change_is_good(
            current_period["overtrading_score"],
            previous_period["overtrading_score"],
        ),
        "post_loss_recovery": calculate_change(
            current_period["post_loss_recovery_score"],
            previous_period["post_loss_recovery_score"],
        ),
    }

    evolution_score = calculate_evolution_score(
        previous_period,
        current_period,
        changes,
    )

    evolution_stage = get_evolution_stage(evolution_score)

    coach_message = build_coach_message(
        previous_period,
        current_period,
        changes,
        evolution_score,
    )

    return {
        "status": "completed",
        "evolution_score": evolution_score,
        "evolution_stage": evolution_stage,
        "previous_period": previous_period,
        "current_period": current_period,
        "changes": changes,
        "coach_message": coach_message,
    }


def build_evolution(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    return generate_evolution_engine(trades)
