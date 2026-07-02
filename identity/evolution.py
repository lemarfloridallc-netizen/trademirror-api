# identity/evolution.py

from typing import Any, Dict, List, Optional


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


def calculate_profit_factor(gross_profit: float, gross_loss: float) -> float:
    gross_profit = safe_float(gross_profit)
    gross_loss = abs(safe_float(gross_loss))

    if gross_loss == 0:
        if gross_profit > 0:
            return 999.0
        return 0.0

    return round(gross_profit / gross_loss, 2)


def split_trades_by_time(trades: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    total = len(trades)

    if total < 2:
        return {
            "previous_period": [],
            "current_period": trades,
        }

    midpoint = total // 2

    return {
        "previous_period": trades[:midpoint],
        "current_period": trades[midpoint:],
    }


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
        }

    gross_profit = 0.0
    gross_loss = 0.0
    winning_trades = 0
    losing_trades = 0
    asset_summary: Dict[str, Dict[str, Any]] = {}

    previous_trade_was_loss = False
    post_loss_trades = 0
    post_loss_wins = 0

    for trade in trades:
        pnl = safe_float(
            trade.get("pnl")
            or trade.get("profit")
            or trade.get("realized_pnl")
            or trade.get("net_pnl")
            or 0
        )

        asset = (
            trade.get("asset")
            or trade.get("symbol")
            or trade.get("ticker")
            or "UNKNOWN"
        )

        if pnl > 0:
            gross_profit += pnl
            winning_trades += 1
        elif pnl < 0:
            gross_loss += pnl
            losing_trades += 1

        if asset not in asset_summary:
            asset_summary[asset] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "net_pnl": 0.0,
                "gross_profit": 0.0,
                "gross_loss": 0.0,
                "profit_factor": 0.0,
            }

        asset_summary[asset]["trades"] += 1
        asset_summary[asset]["net_pnl"] += pnl

        if pnl > 0:
            asset_summary[asset]["wins"] += 1
            asset_summary[asset]["gross_profit"] += pnl
        elif pnl < 0:
            asset_summary[asset]["losses"] += 1
            asset_summary[asset]["gross_loss"] += pnl

        if previous_trade_was_loss:
            post_loss_trades += 1
            if pnl > 0:
                post_loss_wins += 1

        previous_trade_was_loss = pnl < 0

    for asset, data in asset_summary.items():
        data["net_pnl"] = round(data["net_pnl"], 2)
        data["gross_profit"] = round(data["gross_profit"], 2)
        data["gross_loss"] = round(data["gross_loss"], 2)
        data["profit_factor"] = calculate_profit_factor(
            data["gross_profit"],
            data["gross_loss"],
        )

    net_pnl = gross_profit + gross_loss
    win_rate = round((winning_trades / total_trades) * 100, 2)
    profit_factor = calculate_profit_factor(gross_profit, gross_loss)
    capital_leak = abs(gross_loss)

    best_asset = None
    worst_asset = None

    if asset_summary:
        best_asset = max(asset_summary.items(), key=lambda item: item[1]["net_pnl"])[0]
        worst_asset = min(asset_summary.items(), key=lambda item: item[1]["net_pnl"])[0]

    overtrading_score = calculate_overtrading_score(total_trades)
    post_loss_recovery_score = round((post_loss_wins / post_loss_trades) * 100, 2) if post_loss_trades > 0 else 0.0

    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "net_pnl": round(net_pnl, 2),
        "gross_profit": round(gross_profit, 2),
        "gross_loss": round(gross_loss, 2),
        "profit_factor": profit_factor,
        "capital_leak": round(capital_leak, 2),
        "best_asset": best_asset,
        "worst_asset": worst_asset,
        "asset_summary": asset_summary,
        "overtrading_score": overtrading_score,
        "post_loss_recovery_score": post_loss_recovery_score,
    }


def calculate_overtrading_score(total_trades: int) -> float:
    total_trades = safe_int(total_trades)

    if total_trades <= 5:
        return 10.0
    if total_trades <= 10:
        return 25.0
    if total_trades <= 20:
        return 50.0
    if total_trades <= 35:
        return 75.0

    return 100.0


def calculate_change(current: float, previous: float) -> Dict[str, Any]:
    current = safe_float(current)
    previous = safe_float(previous)

    absolute_change = round(current - previous, 2)

    if previous == 0:
        percentage_change = 0.0
    else:
        percentage_change = round(((current - previous) / abs(previous)) * 100, 2)

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


def calculate_evolution_score(changes: Dict[str, Dict[str, Any]]) -> float:
    score = 50.0

    if changes["win_rate"]["direction"] == "improved":
        score += 12
    elif changes["win_rate"]["direction"] == "declined":
        score -= 12

    if changes["profit_factor"]["direction"] == "improved":
        score += 18
    elif changes["profit_factor"]["direction"] == "declined":
        score -= 18

    if changes["capital_leak"]["direction"] == "improved":
        score += 20
    elif changes["capital_leak"]["direction"] == "declined":
        score -= 20

    if changes["overtrading"]["direction"] == "improved":
        score += 15
    elif changes["overtrading"]["direction"] == "declined":
        score -= 15

    if changes["post_loss_recovery"]["direction"] == "improved":
        score += 15
    elif changes["post_loss_recovery"]["direction"] == "declined":
        score -= 15

    return round(max(0.0, min(score, 100.0)), 2)


def get_evolution_stage(score: float) -> str:
    score = safe_float(score)

    if score >= 80:
        return "strong_improvement"
    if score >= 65:
        return "improving"
    if score >= 45:
        return "stable"
    if score >= 30:
        return "declining"

    return "critical_decline"


def build_coach_message(
    previous: Dict[str, Any],
    current: Dict[str, Any],
    changes: Dict[str, Dict[str, Any]],
    score: float,
) -> str:
    improvements = []
    risks = []

    if changes["profit_factor"]["direction"] == "improved":
        improvements.append("tu profit factor está mejorando")

    if changes["win_rate"]["direction"] == "improved":
        improvements.append("tu tasa de acierto está subiendo")

    if changes["capital_leak"]["direction"] == "improved":
        improvements.append("estás reduciendo la fuga de capital")

    if changes["overtrading"]["direction"] == "improved":
        improvements.append("estás operando con más control")

    if changes["post_loss_recovery"]["direction"] == "improved":
        improvements.append("tu comportamiento después de pérdidas está mejorando")

    if changes["capital_leak"]["direction"] == "declined":
        risks.append("la fuga de capital aumentó")

    if changes["overtrading"]["direction"] == "declined":
        risks.append("hay señales de sobreoperación")

    if changes["post_loss_recovery"]["direction"] == "declined":
        risks.append("sigues vulnerable después de una pérdida")

    if current.get("worst_asset"):
        risks.append(f"tu mayor debilidad actual está en {current.get('worst_asset')}")

    if score >= 70:
        base = "Estás mostrando una evolución positiva."
    elif score >= 45:
        base = "Tu evolución está estable, pero todavía necesita más consistencia."
    else:
        base = "Tu evolución muestra señales de deterioro que deben corregirse pronto."

    if improvements:
        base += " Lo más positivo es que " + ", ".join(improvements[:2]) + "."

    if risks:
        base += " El punto más importante a corregir es que " + ", ".join(risks[:2]) + "."

    return base


def generate_evolution_engine(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not trades:
        return {
            "status": "insufficient_data",
            "message": "No hay operaciones suficientes para calcular evolución.",
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

    evolution_score = calculate_evolution_score(changes)
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
