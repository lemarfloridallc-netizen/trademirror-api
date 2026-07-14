"""
MirrorCoach Trade Evidence Builder

Convierte operaciones cerradas reconstruidas en evidencia objetiva
para MirrorCoach.

Este módulo:
- NO llama a OpenAI.
- NO modifica TradingReport.
- NO modifica Identity.
- NO modifica Blueprint.
- NO inventa comportamientos.
- NO interpreta psicológicamente al trader.

Su única responsabilidad es calcular hechos verificables desde
las operaciones reconstruidas.
"""

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional


def _safe_float(value: Any) -> float:
    """
    Convierte un valor a float de manera segura.
    """

    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _safe_text(value: Any, default: str = "UNKNOWN") -> str:
    """
    Devuelve texto limpio o un valor por defecto.
    """

    text = str(value or "").strip()

    return text if text else default


def _parse_date(value: Any) -> Optional[datetime]:
    """
    Convierte trade_date a datetime cuando sea posible.
    """

    text = str(value or "").strip()

    if not text:
        return None

    try:
        return datetime.strptime(
            text[:10],
            "%Y-%m-%d",
        )
    except (TypeError, ValueError):
        return None


def _profit_factor(
    gross_profit: float,
    gross_loss: float,
) -> Optional[float]:
    """
    Calcula profit factor.

    gross_loss debe recibirse como valor absoluto positivo.
    """

    if gross_loss <= 0:
        return None

    return round(
        gross_profit / gross_loss,
        2,
    )


def _summarize_group(
    trades: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Resume una colección de operaciones.
    """

    winners = [
        trade
        for trade in trades
        if _safe_float(
            trade.get("realized_pnl")
        ) > 0
    ]

    losers = [
        trade
        for trade in trades
        if _safe_float(
            trade.get("realized_pnl")
        ) < 0
    ]

    gross_profit = sum(
        _safe_float(
            trade.get("realized_pnl")
        )
        for trade in winners
    )

    gross_loss = abs(
        sum(
            _safe_float(
                trade.get("realized_pnl")
            )
            for trade in losers
        )
    )

    net_pnl = sum(
        _safe_float(
            trade.get("realized_pnl")
        )
        for trade in trades
    )

    total_trades = len(trades)

    win_rate = (
        len(winners) / total_trades * 100
        if total_trades
        else 0
    )

    average_winner = (
        gross_profit / len(winners)
        if winners
        else 0
    )

    average_loser = (
        -gross_loss / len(losers)
        if losers
        else 0
    )

    return {
        "total_trades": total_trades,
        "winning_trades": len(winners),
        "losing_trades": len(losers),
        "win_rate": round(win_rate, 2),
        "net_pnl": round(net_pnl, 2),
        "gross_profit": round(
            gross_profit,
            2,
        ),
        "gross_loss": round(
            gross_loss,
            2,
        ),
        "profit_factor": _profit_factor(
            gross_profit,
            gross_loss,
        ),
        "average_winner": round(
            average_winner,
            2,
        ),
        "average_loser": round(
            average_loser,
            2,
        ),
    }


def _trade_reference(
    trade: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Devuelve una referencia compacta y segura de una operación.
    """

    if not trade:
        return None

    return {
        "trade_date": trade.get(
            "trade_date"
        ),
        "trade_time": trade.get(
            "trade_time"
        ),
        "symbol": trade.get(
            "symbol"
        ),
        "asset": (
            trade.get("asset_base")
            or trade.get("asset")
            or trade.get("ticker")
        ),
        "option_side": trade.get(
            "option_side"
        ),
        "realized_pnl": round(
            _safe_float(
                trade.get("realized_pnl")
            ),
            2,
        ),
        "order_count": trade.get(
            "order_count"
        ),
    }


def build_trade_evidence(
    reconstructed_trades: List[
        Dict[str, Any]
    ],
) -> Dict[str, Any]:
    """
    Construye evidencia operativa objetiva.

    Calcula:
    - mejor y peor operación;
    - mejor y peor día;
    - resultados por activo;
    - resultados por dirección CALL/PUT;
    - resultados por día de la semana;
    - frecuencia diaria;
    - concentración de pérdidas.

    No atribuye causas conductuales.
    """

    trades = [
        trade
        for trade in (
            reconstructed_trades or []
        )
        if isinstance(trade, dict)
    ]

    if not trades:
        return {
            "status": "insufficient_data",
            "total_trades": 0,
            "message": (
                "No reconstructed trades are available."
            ),
        }

    # -----------------------------------------
    # Operaciones individuales
    # -----------------------------------------

    best_trade = max(
        trades,
        key=lambda trade: _safe_float(
            trade.get("realized_pnl")
        ),
    )

    worst_trade = min(
        trades,
        key=lambda trade: _safe_float(
            trade.get("realized_pnl")
        ),
    )

    # -----------------------------------------
    # Agrupaciones
    # -----------------------------------------

    trades_by_date = defaultdict(list)
    trades_by_asset = defaultdict(list)
    trades_by_side = defaultdict(list)
    trades_by_weekday = defaultdict(list)

    for trade in trades:
        trade_date = _safe_text(
            trade.get("trade_date")
        )

        asset = _safe_text(
            trade.get("asset_base")
            or trade.get("asset")
            or trade.get("ticker")
        )

        option_side = _safe_text(
            trade.get("option_side")
        )

        parsed_date = _parse_date(
            trade.get("trade_date")
        )

        weekday = (
            parsed_date.strftime("%A")
            if parsed_date
            else "UNKNOWN"
        )

        trades_by_date[
            trade_date
        ].append(trade)

        trades_by_asset[
            asset
        ].append(trade)

        trades_by_side[
            option_side
        ].append(trade)

        trades_by_weekday[
            weekday
        ].append(trade)

    # -----------------------------------------
    # Días
    # -----------------------------------------

    daily_results = {
        trade_date: {
            "trade_date": trade_date,
            **_summarize_group(
                day_trades
            ),
        }
        for trade_date, day_trades
        in trades_by_date.items()
    }

    best_day = max(
        daily_results.values(),
        key=lambda item: item["net_pnl"],
    )

    worst_day = min(
        daily_results.values(),
        key=lambda item: item["net_pnl"],
    )

    most_active_day = max(
        daily_results.values(),
        key=lambda item: item["total_trades"],
    )

    # -----------------------------------------
    # Activos
    # -----------------------------------------

    asset_results = {
        asset: _summarize_group(
            asset_trades
        )
        for asset, asset_trades
        in trades_by_asset.items()
    }

    best_asset_name = max(
        asset_results,
        key=lambda name: (
            asset_results[name]["net_pnl"]
        ),
    )

    worst_asset_name = min(
        asset_results,
        key=lambda name: (
            asset_results[name]["net_pnl"]
        ),
    )

    # -----------------------------------------
    # CALL / PUT
    # -----------------------------------------

    side_results = {
        side: _summarize_group(
            side_trades
        )
        for side, side_trades
        in trades_by_side.items()
    }

    # -----------------------------------------
    # Día de semana
    # -----------------------------------------

    weekday_results = {
        weekday: _summarize_group(
            weekday_trades
        )
        for weekday, weekday_trades
        in trades_by_weekday.items()
    }

    valid_weekdays = {
        weekday: data
        for weekday, data
        in weekday_results.items()
        if weekday != "UNKNOWN"
    }

    best_weekday = None
    worst_weekday = None

    if valid_weekdays:
        best_weekday_name = max(
            valid_weekdays,
            key=lambda name: (
                valid_weekdays[name]["net_pnl"]
            ),
        )

        worst_weekday_name = min(
            valid_weekdays,
            key=lambda name: (
                valid_weekdays[name]["net_pnl"]
            ),
        )

        best_weekday = {
            "weekday": best_weekday_name,
            **valid_weekdays[
                best_weekday_name
            ],
        }

        worst_weekday = {
            "weekday": worst_weekday_name,
            **valid_weekdays[
                worst_weekday_name
            ],
        }

    # -----------------------------------------
    # Concentración de pérdidas
    # -----------------------------------------

    losing_trades = sorted(
        (
            trade
            for trade in trades
            if _safe_float(
                trade.get("realized_pnl")
            ) < 0
        ),
        key=lambda trade: _safe_float(
            trade.get("realized_pnl")
        ),
    )

    total_gross_loss = abs(
        sum(
            _safe_float(
                trade.get("realized_pnl")
            )
            for trade in losing_trades
        )
    )

    largest_five_losses = (
        losing_trades[:5]
    )

    largest_five_loss_total = abs(
        sum(
            _safe_float(
                trade.get("realized_pnl")
            )
            for trade in largest_five_losses
        )
    )

    largest_five_loss_share = (
        largest_five_loss_total
        / total_gross_loss
        * 100
        if total_gross_loss
        else 0
    )

    # -----------------------------------------
    # Resultado final
    # -----------------------------------------

    return {
        "status": "completed",
        "evidence_version": 1,

        "overall": _summarize_group(
            trades
        ),

        "best_trade": _trade_reference(
            best_trade
        ),

        "worst_trade": _trade_reference(
            worst_trade
        ),

        "best_day": best_day,
        "worst_day": worst_day,
        "most_active_day": most_active_day,

        "best_asset": {
            "asset": best_asset_name,
            **asset_results[
                best_asset_name
            ],
        },

        "worst_asset": {
            "asset": worst_asset_name,
            **asset_results[
                worst_asset_name
            ],
        },

        "by_asset": asset_results,
        "by_option_side": side_results,
        "by_weekday": weekday_results,

        "best_weekday": best_weekday,
        "worst_weekday": worst_weekday,

        "frequency": {
            "trading_days": len(
                daily_results
            ),
            "average_trades_per_day": round(
                len(trades)
                / len(daily_results),
                2,
            )
            if daily_results
            else 0,
            "maximum_trades_in_one_day": (
                most_active_day[
                    "total_trades"
                ]
            ),
        },

        "loss_concentration": {
            "gross_loss": round(
                total_gross_loss,
                2,
            ),
            "largest_five_losses_total": round(
                largest_five_loss_total,
                2,
            ),
            "largest_five_losses_share_pct": round(
                largest_five_loss_share,
                2,
            ),
            "largest_five_losses": [
                _trade_reference(
                    trade
                )
                for trade
                in largest_five_losses
            ],
        },
    }
