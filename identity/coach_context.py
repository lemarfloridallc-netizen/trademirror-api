"""
MirrorCoach Context Builder V2

Construye un contexto estructurado para MirrorCoach utilizando
exclusivamente información real ya generada por MirrorTrader.

Este módulo:
- NO llama a OpenAI.
- NO modifica métricas.
- NO genera una identidad.
- NO genera un Blueprint.
- NO inventa información.
- NO modifica los análisis existentes.
"""

from typing import Any, Dict, Iterable, Optional


def _safe_dict(value: Any) -> Dict[str, Any]:
    """
    Garantiza que el valor recibido sea un diccionario.
    """

    return value if isinstance(value, dict) else {}


def _first_present(
    source: Dict[str, Any],
    keys: Iterable[str],
    default: Any = None,
) -> Any:
    """
    Devuelve el primer valor existente y no vacío.

    Permite compatibilidad entre nombres actuales y anteriores
    de los campos producidos por MirrorTrader.
    """

    for key in keys:
        value = source.get(key)

        if value not in (
            None,
            "",
            {},
            [],
        ):
            return value

    return default


def build_coach_context(
    metrics: Dict[str, Any],
    identity_payload: Dict[str, Any],
    mirror_law: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Construye el paquete completo de evidencia para MirrorCoach.

    Args:
        metrics:
            Métricas originales calculadas desde el TradingReport.

        identity_payload:
            Resultado completo de build_trading_identity().
            Puede contener Identity, Blueprint, Mirror Insight,
            Evolution y señales conductuales.

        mirror_law:
            Resultado opcional de build_mirror_law_analysis().

    Returns:
        Contexto estructurado listo para clasificación,
        selección de evidencia y envío a OpenAI.
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

    behavioral_signals = _first_present(
        identity_payload,
        (
            "behavioral_signals",
            "behavior_signals",
            "signals",
        ),
        default=[],
    )

    signal_confidences = _first_present(
        identity_payload,
        (
            "signal_confidences",
            "behavioral_signal_confidences",
        ),
        default={},
    )

    identity = {
        "name": _first_present(
            identity_payload,
            (
                "identity_name",
                "identity_name_text",
                "name",
            ),
        ),
        "code": _first_present(
            identity_payload,
            (
                "identity_code",
                "code",
            ),
        ),
        "description": _first_present(
            identity_payload,
            (
                "identity_description",
                "identity_description_text",
                "description",
            ),
        ),
        "match_percentage": _first_present(
            identity_payload,
            (
                "identity_match_percentage",
                "match_percentage",
                "confidence_score",
                "confidence_score_number",
            ),
        ),
        "edge_score": _first_present(
            identity_payload,
            (
                "edge_score",
                "edge_score_number",
            ),
        ),
        "confidence_score": _first_present(
            identity_payload,
            (
                "confidence_score",
                "confidence_score_number",
            ),
        ),
        "identity_version": _first_present(
            identity_payload,
            (
                "identity_version",
                "version",
            ),
        ),
        "reports_analyzed": _first_present(
            identity_payload,
            (
                "reports_analyzed",
                "reports_analyzed_number",
            ),
        ),
        "scores": {
            "discipline": _first_present(
                identity_payload,
                (
                    "discipline_score",
                    "discipline_score_number",
                ),
            ),
            "patience": _first_present(
                identity_payload,
                (
                    "patience_score",
                    "patience_score_number",
                ),
            ),
            "execution": _first_present(
                identity_payload,
                (
                    "execution_score",
                    "execution_score_number",
                ),
            ),
            "selection": _first_present(
                identity_payload,
                (
                    "selection_score",
                    "selection_score_number",
                ),
            ),
            "psychology": _first_present(
                identity_payload,
                (
                    "psychology_score",
                    "psychology_score_number",
                ),
            ),
            "consistency": _first_present(
                identity_payload,
                (
                    "consistency_score",
                    "consistency_score_number",
                ),
            ),
            "risk_management": _first_present(
                identity_payload,
                (
                    "risk_management_score",
                    "risk_management_score_number",
                ),
            ),
            "adaptability": _first_present(
                identity_payload,
                (
                    "adaptability_score",
                    "adaptability_score_number",
                ),
            ),
            "statistical_edge": _first_present(
                identity_payload,
                (
                    "statistical_edge_score",
                    "statistical_edge_score_number",
                ),
            ),
            "evolution": _first_present(
                identity_payload,
                (
                    "evolution_score",
                    "evolution_score_number",
                ),
            ),
        },
    }

    report = {
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
        "asset_breakdown": metrics.get(
            "asset_breakdown",
            {},
        ),
        "symbol_breakdown": metrics.get(
            "symbol_breakdown",
            {},
        ),
        "side_breakdown": metrics.get(
            "side_breakdown",
            {},
        ),
        "broker_source": metrics.get(
            "broker_source"
        ),
        "analysis_date": metrics.get(
            "analysis_date"
        ),
        "processing_status": metrics.get(
            "processing_status"
        ),
    }

    return {
        "context_version": 2,

        "source_policy": {
            "primary_source": (
                "trader_historical_data"
            ),
            "allow_invented_statistics": False,
            "allow_generic_advice_without_disclosure": False,
            "require_evidence_based_answers": True,
        },

        # Resumen estable del reporte.
        "report": report,

        # Métricas completas para evitar perder evidencia
        # que el selector o futuras preguntas necesiten.
        "metrics": metrics,

        "identity": identity,

        # Sección independiente porque evidence_selector.py
        # la busca directamente.
        "behavioral_signals": behavioral_signals,

        "signal_confidences": signal_confidences,

        # Se conservan completos; no eliminamos campos
        # producidos por los motores actuales.
        "blueprint": blueprint,
        "mirror_insight": mirror_insight,
        "evolution": evolution,
        "mirror_law": mirror_law,

        "coach_rules": [
            (
                "Answer primarily from the trader's own "
                "historical evidence."
            ),
            (
                "Never invent statistics, patterns, trades, "
                "behaviors, or conclusions."
            ),
            (
                "Use metrics as evidence, not as behavioral "
                "conclusions."
            ),
            (
                "Identify the personal evidence supporting "
                "every important recommendation."
            ),
            (
                "Do not present general trading knowledge as "
                "personal evidence."
            ),
            (
                "When evidence is incomplete, provide the "
                "strongest supported reflection and establish "
                "a useful baseline."
            ),
            (
                "Never predict markets, promise profits, or "
                "guarantee future results."
            ),
            (
                "Confront deviations from the trader's "
                "demonstrated process directly and respectfully."
            ),
        ],
    }
