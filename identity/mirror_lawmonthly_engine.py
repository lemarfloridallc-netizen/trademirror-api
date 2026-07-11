"""
Mirror Law - Monthly Engine

Analyzes normalized trades by calendar month.

This first version only:
- Groups trades by month.
- Calculates monthly performance metrics.
- Returns all months in chronological order.

It does NOT:
- Select the best month.
- Generate Mirror Law rules.
- Modify the current Blueprint.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from typing import Any, Dict, List, Optional


DATE_FIELDS = (
    "trade_date",
    "date",
    "close_date",
    "exit_date",
    "trade_datetime",
    "datetime",
)

PNL_FIELDS = (
    "net_pnl",
    "pnl",
    "realized_pnl",
    "profit_loss",
    "profit",
)


def _get_first_value(
    trade: Dict[str, Any],
    possible_fields: tuple[str, ...],
) -> Any:
    """
    Returns the first available non-empty field value.
    """

    for field_name in possible_fields:
        value = trade.get(field_name)

        if value is not None and value != "":
            return value

    return None


def _parse_date(value: Any) -> Optional[datetime]:
    """
    Converts common date values into a datetime object.
    """

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    formats = (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%m/%d/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M:%S",
    )

    for date_format in formats:
        try:
            return datetime.strptime(text, date_format)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(
            text.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def _parse_number(value: Any) -> Optional[float]:
    """
    Converts numbers and common currency strings into float values.
    """

    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if not text:
        return None

    parenthesized_negative = (
        text.startswith("(")
        and text.endswith(")")
    )

    cleaned = (
        text.replace("$", "")
        .replace(",", "")
        .replace("%", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )

    try:
        number = float(cleaned)
    except ValueError:
        return None

    if parenthesized_negative:
        number = -abs(number)

    return number


def _round_number(value: float, decimals: int = 2) -> float:
    """
    Rounds output values and prevents negative zero.
    """

    result = round(float(value), decimals)

    if result == 0:
        return 0.0

    return result


def build_monthly_metrics(
    trades: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Groups normalized trades by calendar month.

    Args:
        trades:
            List of normalized trade dictionaries.

    Returns:
        Dictionary containing:
        - months
        - total_months
        - valid_trades
        - ignored_trades
    """

    grouped_trades: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    valid_trades = 0
    ignored_trades = 0

    for trade in trades:

        if not isinstance(trade, dict):
            ignored_trades += 1
            continue

        raw_date = _get_first_value(
            trade,
            DATE_FIELDS,
        )

        raw_pnl = _get_first_value(
            trade,
            PNL_FIELDS,
        )

        trade_datetime = _parse_date(raw_date)
        trade_pnl = _parse_number(raw_pnl)

        if trade_datetime is None or trade_pnl is None:
            ignored_trades += 1
            continue

        month_key = trade_datetime.strftime("%Y-%m")

        grouped_trades[month_key].append(
            {
                "trade_datetime": trade_datetime,
                "trade_date": trade_datetime.date(),
                "net_pnl": trade_pnl,
            }
        )

        valid_trades += 1

    months: List[Dict[str, Any]] = []

    for month_key in sorted(grouped_trades.keys()):

        month_trades = grouped_trades[month_key]

        pnl_values = [
            trade["net_pnl"]
            for trade in month_trades
        ]

        winning_trades = [
            pnl
            for pnl in pnl_values
            if pnl > 0
        ]

        losing_trades = [
            pnl
            for pnl in pnl_values
            if pnl < 0
        ]

        breakeven_trades = [
            pnl
            for pnl in pnl_values
            if pnl == 0
        ]

        trades_by_day: Dict[date, int] = defaultdict(int)

        for trade in month_trades:
            trades_by_day[trade["trade_date"]] += 1

        total_trades = len(pnl_values)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        breakeven_count = len(breakeven_trades)

        gross_profit = sum(winning_trades)
        gross_loss = sum(losing_trades)
        net_pnl = sum(pnl_values)

        win_rate = (
            winning_count / total_trades * 100
            if total_trades
            else 0
        )

        average_winner = (
            gross_profit / winning_count
            if winning_count
            else 0
        )

        average_loser = (
            gross_loss / losing_count
            if losing_count
            else 0
        )

        profit_factor = (
            gross_profit / abs(gross_loss)
            if gross_loss < 0
            else None
        )

        expectancy = (
            net_pnl / total_trades
            if total_trades
            else 0
        )

        trading_days = len(trades_by_day)

        average_trades_per_day = (
            total_trades / trading_days
            if trading_days
            else 0
        )

        max_trades_in_one_day = (
            max(trades_by_day.values())
            if trades_by_day
            else 0
        )

        first_trade_date = min(
            trade["trade_date"]
            for trade in month_trades
        )

        last_trade_date = max(
            trade["trade_date"]
            for trade in month_trades
        )

        first_trade_datetime = min(
            trade["trade_datetime"]
            for trade in month_trades
        )

        month_result = {
            "month_key": month_key,
            "month_label": first_trade_datetime.strftime("%B %Y"),
            "month_start": first_trade_date.isoformat(),
            "month_end": last_trade_date.isoformat(),
            "total_trades": total_trades,
            "winning_trades": winning_count,
            "losing_trades": losing_count,
            "breakeven_trades": breakeven_count,
            "net_pnl": _round_number(net_pnl),
            "gross_profit": _round_number(gross_profit),
            "gross_loss": _round_number(gross_loss),
            "win_rate": _round_number(win_rate),
            "average_winner": _round_number(average_winner),
            "average_loser": _round_number(average_loser),
            "profit_factor": (
                _round_number(profit_factor)
                if profit_factor is not None
                else None
            ),
            "expectancy": _round_number(expectancy),
            "best_trade": _round_number(max(pnl_values)),
            "worst_trade": _round_number(min(pnl_values)),
            "trading_days": trading_days,
            "average_trades_per_day": _round_number(
                average_trades_per_day
            ),
            "max_trades_in_one_day": max_trades_in_one_day,
        }

        months.append(month_result)

    return {
        "months": months,
        "total_months": len(months),
        "valid_trades": valid_trades,
        "ignored_trades": ignored_trades,
    }
