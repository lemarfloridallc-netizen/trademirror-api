"""
Mirror Law - Trade Reconstruction Engine

Reconstructs dated trades from the existing IBKR parser output.

IBKR currently provides:
- Orders with date, time, symbol, quantity and price.
- Closed trade subtotals with final realized P&L but no date.

This engine joins both records using the complete contract symbol.

It does not modify:
- The existing parser.
- Identity.
- Blueprint.
- Monthly Engine.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional


def _parse_datetime(date_value: Any, time_value: Any = None) -> Optional[datetime]:
    """
    Converts the existing order date and time fields into datetime.
    """

    if isinstance(date_value, datetime):
        return date_value

    if date_value is None:
        return None

    date_text = str(date_value).strip()
    time_text = str(time_value).strip() if time_value else ""

    if not date_text:
        return None

    combined_text = (
        f"{date_text} {time_text}"
        if time_text
        else date_text
    )

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
    )

    for date_format in formats:
        try:
            return datetime.strptime(
                combined_text,
                date_format,
            )
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(
            combined_text.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def _normalize_symbol(value: Any) -> str:
    """
    Normalizes contract symbols without changing their meaning.
    """

    if value is None:
        return ""

    return " ".join(
        str(value).strip().upper().split()
    )


def _to_float(value: Any) -> float:
    """
    Safely converts values into floats.
    """

    if value is None or isinstance(value, bool):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if not text or text == "--":
        return 0.0

    parenthesized_negative = (
        text.startswith("(")
        and text.endswith(")")
    )

    cleaned = (
        text.replace("$", "")
        .replace(",", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )

    try:
        number = float(cleaned)
    except ValueError:
        return 0.0

    if parenthesized_negative:
        return -abs(number)

    return number


def reconstruct_closed_trades(
    orders: List[Dict[str, Any]],
    closed_trades: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Joins dated IBKR orders with final closed-trade subtotals.

    Matching method:
    - Exact normalized contract symbol.
    - The reconstructed trade date is the latest valid order date
      associated with that exact contract.

    The latest date is used because realized P&L is normally recognized
    when the position is closed.

    Returns:
        {
            "trades": [...],
            "reconstructed_trades": int,
            "unmatched_closed_trades": [...],
            "symbols_with_orders_only": [...],
        }
    """

    orders_by_symbol: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for order in orders:
        if not isinstance(order, dict):
            continue

        symbol = _normalize_symbol(
            order.get("symbol")
        )

        if not symbol:
            continue

        trade_datetime = _parse_datetime(
            order.get("date"),
            order.get("time"),
        )

        if trade_datetime is None:
            continue

        orders_by_symbol[symbol].append(
            {
                **order,
                "_trade_datetime": trade_datetime,
            }
        )

    for symbol_orders in orders_by_symbol.values():
        symbol_orders.sort(
            key=lambda item: item["_trade_datetime"]
        )

    reconstructed_trades: List[Dict[str, Any]] = []
    unmatched_closed_trades: List[Dict[str, Any]] = []
    matched_symbols = set()

    for closed_trade in closed_trades:
        if not isinstance(closed_trade, dict):
            continue

        symbol = _normalize_symbol(
            closed_trade.get("symbol")
        )

        matching_orders = orders_by_symbol.get(
            symbol,
            [],
        )

        if not symbol or not matching_orders:
            unmatched_closed_trades.append(
                closed_trade
            )
            continue

        matched_symbols.add(symbol)

        first_order = matching_orders[0]
        last_order = matching_orders[-1]

        first_datetime = first_order["_trade_datetime"]
        last_datetime = last_order["_trade_datetime"]

        realized_pnl = _to_float(
            closed_trade.get(
                "realized_pnl",
                closed_trade.get("pnl", 0),
            )
        )

        commission = _to_float(
            closed_trade.get("commission", 0)
        )

        reconstructed_trades.append(
            {
                "trade_date": last_datetime.date().isoformat(),
                "trade_time": last_datetime.time().isoformat(),
                "trade_datetime": last_datetime.isoformat(),
                "first_order_datetime": first_datetime.isoformat(),
                "last_order_datetime": last_datetime.isoformat(),
                "symbol": closed_trade.get(
                    "symbol",
                    last_order.get("symbol"),
                ),
                "asset_base": closed_trade.get(
                    "asset_base",
                    last_order.get("asset_base", "UNKNOWN"),
                ),
                "asset": closed_trade.get(
                    "asset",
                    last_order.get("asset_base", "UNKNOWN"),
                ),
                "ticker": closed_trade.get(
                    "ticker",
                    last_order.get("asset_base", "UNKNOWN"),
                ),
                "option_side": closed_trade.get(
                    "option_side",
                    last_order.get("option_side", "UNKNOWN"),
                ),
                "realized_pnl": realized_pnl,
                "pnl": realized_pnl,
                "transaction_pnl": _to_float(
                    closed_trade.get("transaction_pnl", 0)
                ),
                "commission": commission,
                "order_count": len(matching_orders),
                "total_absolute_quantity": round(
                    sum(
                        abs(
                            _to_float(
                                order.get("quantity", 0)
                            )
                        )
                        for order in matching_orders
                    ),
                    4,
                ),
                "first_price": _to_float(
                    first_order.get("price", 0)
                ),
                "last_price": _to_float(
                    last_order.get("price", 0)
                ),
                "reconstruction_method": (
                    "exact_symbol_latest_order_date"
                ),
            }
        )

    symbols_with_orders_only = sorted(
        symbol
        for symbol in orders_by_symbol
        if symbol not in matched_symbols
    )

    reconstructed_trades.sort(
        key=lambda trade: trade["trade_datetime"]
    )

    return {
        "trades": reconstructed_trades,
        "reconstructed_trades": len(
            reconstructed_trades
        ),
        "unmatched_closed_trades": (
            unmatched_closed_trades
        ),
        "unmatched_closed_trades_count": len(
            unmatched_closed_trades
        ),
        "symbols_with_orders_only": (
            symbols_with_orders_only
        ),
        "symbols_with_orders_only_count": len(
            symbols_with_orders_only
        ),
    }
