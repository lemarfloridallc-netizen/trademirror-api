"""
MirrorCoach Context Builder

Construye un contexto estructurado para el AI Coach utilizando únicamente
información ya generada por MirrorTrader.

Este módulo:
- NO llama a OpenAI.
- NO modifica métricas.
- NO genera una nueva identidad.
- NO genera un nuevo blueprint.
- NO inventa información.
- NO modifica el pipeline existente.
"""

from typing import Any, Dict


def _safe_dict(value: Any) -> Dict[str, Any]:
    """
    Garantiza que el valor recibido sea un diccionario.
    """
    return value if isinstance(value, dict) else {}


def build_coach_context(
    metrics: Dict[str, Any],
    identity_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Construye el contexto estructurado que utilizará MirrorCoach.

    Args:
        metrics:
            Métricas originales del TradingReport.

        identity_payload:
            Resultado generado por build_trading_identity().
            Ya contiene Identity, Blueprint, Mirror Insight y Evolution.

    Returns:
        Diccionario estructurado y listo para utilizarse posteriormente
        en el AI Coach.
    """

    metrics = _safe_dict(metrics)
    identity_payload = _safe_dict(identity_payload)

    blueprint = _safe_dict(identity_payload.get("blueprint"))
    mirror_insight = _safe_dict(identity_payload.get("mirror_insight"))
    evolution = _safe_dict(identity_payload.get("evolution"))

    coach_context = {
        "context_version": 1,

        "source_policy": {
            "primary_source": "trader_historical_data",
            "allow_invented_statistics": False,
            "allow_generic_advice_without_disclosure": False,
            "require_evidence_based_answers": True,
        },

        "report": {
            "total_trades": metrics.get("total_trades"),
            "win_rate": metrics.get("win_rate"),
            "profit_factor": metrics.get("profit_factor"),
            "net_pnl": metrics.get("net_pnl"),
            "gross_profit": metrics.get("gross_profit"),
            "gross_loss": metrics.get("gross_loss"),
            "average_winner": metrics.get("average_winner"),
            "average_loser": metrics.get("average_loser"),
            "best_asset": metrics.get("best_asset"),
            "best_asset_gains": metrics.get("best_asset_gains"),
            "worst_asset": metrics.get("worst_asset"),
            "worst_asset_pnl": metrics.get("worst_asset_pnl"),
            "broker_source": metrics.get("broker_source"),
            "analysis_date": metrics.get("analysis_date"),
            "processing_status": metrics.get("processing_status"),
        },

        "identity": {
            "name": identity_payload.get("identity_name"),
            "code": identity_payload.get("identity_code"),
            "description": identity_payload.get("identity_description"),
            "match_percentage": identity_payload.get(
                "identity_match_percentage"
            ),
            "edge_score": identity_payload.get("edge_score"),
            "confidence_score": identity_payload.get("confidence_score"),
            "identity_version": identity_payload.get("identity_version"),
            "reports_analyzed": identity_payload.get("reports_analyzed"),

            "scores": {
                "discipline": identity_payload.get("discipline_score"),
                "patience": identity_payload.get("patience_score"),
                "execution": identity_payload.get("execution_score"),
                "selection": identity_payload.get("selection_score"),
                "psychology": identity_payload.get("psychology_score"),
                "consistency": identity_payload.get("consistency_score"),
                "risk_management": identity_payload.get(
                    "risk_management_score"
                ),
                "adaptability": identity_payload.get("adaptability_score"),
                "statistical_edge": identity_payload.get(
                    "statistical_edge_score"
                ),
            },

            "behavioral_signals": identity_payload.get(
                "behavioral_signals",
                [],
            ),
            "signal_confidences": identity_payload.get(
                "signal_confidences",
                {},
            ),
        },

        "blueprint": blueprint,

        "mirror_insight": {
            "headline": mirror_insight.get("headline"),
            "main_observation": mirror_insight.get("main_observation"),
            "risk_warning": mirror_insight.get("risk_warning"),
            "today_focus": mirror_insight.get("today_focus"),
        },

        "evolution": evolution,

        "coach_rules": [
            (
                "Answer primarily from the trader's own report, identity, "
                "blueprint, behavioral signals, and evolution data."
            ),
            "Never invent statistics, patterns, trades, or conclusions.",
            (
                "When making a recommendation, identify the personal evidence "
                "that supports it."
            ),
            (
                "Do not present generic trading knowledge as if it were proven "
                "by this trader's data."
            ),
            (
                "If the available context cannot answer the question, say so "
                "clearly."
            ),
            (
                "Never promise profits, certainty, or future market outcomes."
            ),
            (
                "Confront harmful deviations from the trader's demonstrated "
                "process directly and respectfully."
            ),
        ],
    }

    return coach_context
