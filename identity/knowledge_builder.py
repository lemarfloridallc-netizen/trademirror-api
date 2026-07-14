"""
Mirror Knowledge Base Builder

Construye una base de conocimiento estructurada para MirrorCoach
utilizando únicamente información ya generada por MirrorTrader.

Este módulo:
- NO llama a OpenAI.
- NO modifica TradingReport.
- NO modifica Identity.
- NO modifica Blueprint.
- NO recalcula métricas.
- NO inventa información.
- NO reemplaza Coach Context todavía.

Su responsabilidad es organizar toda la evidencia disponible
en una estructura única, clara y escalable.
"""

from typing import Any, Dict


def _safe_dict(value: Any) -> Dict[str, Any]:
    """
    Garantiza que el valor recibido sea un diccionario.
    """

    return value if isinstance(value, dict) else {}


def build_mirror_knowledge_base(
    metrics: Dict[str, Any],
    identity_payload: Dict[str, Any],
    mirror_law: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Construye la Mirror Knowledge Base completa.

    Args:
        metrics:
            Métricas calculadas desde el CSV.

        identity_payload:
            Resultado completo de build_trading_identity().

        mirror_law:
            Resultado del pipeline de reconstrucción,
            métricas mensuales y trade evidence.

    Returns:
        Diccionario estructurado listo para ser almacenado,
        consultado o filtrado antes de enviarlo a OpenAI.
    """

    metrics = _safe_dict(metrics)
    identity_payload = _safe_dict(
        identity_payload
    )
    mirror_law = _safe_dict(
        mirror_law
    )

    blueprint = _safe_dict(
        identity_payload.get("blueprint")
    )

    mirror_insight = _safe_dict(
        identity_payload.get("mirror_insight")
    )

    evolution = _safe_dict(
        identity_payload.get("evolution")
    )

    trade_evidence = _safe_dict(
        mirror_law.get("trade_evidence")
    )

    reconstructed_trades = (
        mirror_law.get(
            "reconstructed_trades",
            [],
        )
    )

    if not isinstance(
        reconstructed_trades,
        list,
    ):
        reconstructed_trades = []

    months = mirror_law.get(
        "months",
        [],
    )

    if not isinstance(months, list):
        months = []

    return {
        "knowledge_version": 1,

        "source": {
            "type": "trader_historical_data",
            "broker": metrics.get(
                "broker_source"
            ),
            "analysis_date": metrics.get(
                "analysis_date"
            ),
            "processing_status": metrics.get(
                "processing_status"
            ),
        },

        "integrity": {
            "allow_invented_statistics": False,
            "allow_invented_trades": False,
            "allow_invented_behaviors": False,
            "require_evidence_traceability": True,
        },

        "report": {
            "total_trades": metrics.get(
                "total_trades"
            ),
            "winning_trades": metrics.get(
                "winning_trades"
            ),
            "losing_trades": metrics.get(
                "losing_trades"
            ),
            "win_rate": metrics.get(
                "win_rate"
            ),
            "profit_factor": metrics.get(
                "profit_factor"
            ),
            "net_pnl": metrics.get(
                "net_pnl"
            ),
            "gross_profit": metrics.get(
                "gross_profit"
            ),
            "gross_loss": metrics.get(
                "gross_loss"
            ),
            "average_winner": metrics.get(
                "average_winner"
            ),
            "average_loser": metrics.get(
                "average_loser"
            ),
            "best_asset": metrics.get(
                "best_asset"
            ),
            "best_asset_pnl": metrics.get(
                "best_asset_pnl"
            ),
            "worst_asset": metrics.get(
                "worst_asset"
            ),
            "worst_asset_pnl": metrics.get(
                "worst_asset_pnl"
            ),
            "best_trade": metrics.get(
                "best_trade"
            ),
            "worst_trade": metrics.get(
                "worst_trade"
            ),
            "starting_capital": metrics.get(
                "starting_capital"
            ),
            "ending_capital": metrics.get(
                "ending_capital"
            ),
            "commissions_total": metrics.get(
                "commissions_total"
            ),
            "period_return": metrics.get(
                "period_return"
            ),
        },

        "metrics": metrics,

        "identity": {
            "name": identity_payload.get(
                "identity_name"
            ),
            "code": identity_payload.get(
                "identity_code"
            ),
            "description": identity_payload.get(
                "identity_description"
            ),
            "match_percentage": (
                identity_payload.get(
                    "identity_match_percentage"
                )
            ),
            "edge_score": identity_payload.get(
                "edge_score"
            ),
            "confidence_score": (
                identity_payload.get(
                    "confidence_score"
                )
            ),
            "identity_version": (
                identity_payload.get(
                    "identity_version"
                )
            ),
            "reports_analyzed": (
                identity_payload.get(
                    "reports_analyzed"
                )
            ),
            "scores": {
                "discipline": (
                    identity_payload.get(
                        "discipline_score"
                    )
                ),
                "patience": (
                    identity_payload.get(
                        "patience_score"
                    )
                ),
                "execution": (
                    identity_payload.get(
                        "execution_score"
                    )
                ),
                "selection": (
                    identity_payload.get(
                        "selection_score"
                    )
                ),
                "psychology": (
                    identity_payload.get(
                        "psychology_score"
                    )
                ),
                "consistency": (
                    identity_payload.get(
                        "consistency_score"
                    )
                ),
                "risk_management": (
                    identity_payload.get(
                        "risk_management_score"
                    )
                ),
                "adaptability": (
                    identity_payload.get(
                        "adaptability_score"
                    )
                ),
                "statistical_edge": (
                    identity_payload.get(
                        "statistical_edge_score"
                    )
                ),
                "evolution": (
                    identity_payload.get(
                        "evolution_score"
                    )
                ),
            },
        },

        "behavioral_signals": (
            identity_payload.get(
                "behavioral_signals",
                [],
            )
        ),

        "signal_confidences": (
            identity_payload.get(
                "signal_confidences",
                {},
            )
        ),

        "blueprint": {
            "status": (
                "provisional_identity_guidance"
            ),
            "data": blueprint,
            "evidence_warning": (
                "Some Blueprint rules may be identity-based "
                "guidance rather than statistically validated "
                "behavior from the CSV."
            ),
        },

        "mirror_insight": mirror_insight,

        "evolution": evolution,

        "monthly_analysis": {
            "months": months,
            "total_months": mirror_law.get(
                "total_months",
                0,
            ),
            "valid_trades": mirror_law.get(
                "valid_trades",
                0,
            ),
            "ignored_trades": mirror_law.get(
                "ignored_trades",
                0,
            ),
        },

        "trade_evidence": trade_evidence,

        "trade_history": {
            "total_reconstructed_trades": len(
                reconstructed_trades
            ),
            "reconstructed_trades": (
                reconstructed_trades
            ),
        },

        "reconstruction_quality": (
            mirror_law.get(
                "reconstruction",
                {},
            )
        ),
    }
