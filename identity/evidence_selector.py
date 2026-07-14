"""
MirrorCoach Evidence Selector

Selecciona la evidencia relevante para cada tipo de pregunta y garantiza
que la Mirror Knowledge Base permanezca disponible para MirrorCoach.

Este módulo:
- No llama a OpenAI.
- No modifica TradingReport.
- No modifica TradingIdentity.
- No modifica TradingBlueprint.
- No modifica Coach Context.
- No genera respuestas.
- No altera el pipeline existente.

Su responsabilidad es:
1. Normalizar el contexto recibido.
2. Seleccionar las secciones relevantes por categoría.
3. Conservar siempre la Mirror Knowledge Base cuando exista.
4. Informar qué evidencia estaba disponible y qué faltaba.
"""

from typing import Any, Dict, Iterable

from identity.question_classifier import (
    QUESTION_CATEGORY_BLUEPRINT,
    QUESTION_CATEGORY_EDGE_PROTECTION,
    QUESTION_CATEGORY_EDGE_REDUCERS,
    QUESTION_CATEGORY_EVOLUTION,
    QUESTION_CATEGORY_GENERAL,
    QUESTION_CATEGORY_IDENTITY_EVIDENCE,
    QUESTION_CATEGORY_IDENTITY_STRENGTH,
    QUESTION_CATEGORY_IDENTITY_WEAKNESS,
    QUESTION_CATEGORY_LOSS_ANALYSIS,
    QUESTION_CATEGORY_MIRROR_LAW,
)


CATEGORY_EVIDENCE_MAP = {
    QUESTION_CATEGORY_IDENTITY_STRENGTH: (
        "report",
        "metrics",
        "identity",
        "mirror_insight",
        "behavioral_signals",
    ),

    QUESTION_CATEGORY_IDENTITY_WEAKNESS: (
        "report",
        "metrics",
        "identity",
        "mirror_insight",
        "behavioral_signals",
        "blueprint",
    ),

    QUESTION_CATEGORY_IDENTITY_EVIDENCE: (
        "report",
        "metrics",
        "identity",
        "mirror_insight",
        "behavioral_signals",
    ),

    QUESTION_CATEGORY_BLUEPRINT: (
        "report",
        "metrics",
        "identity",
        "blueprint",
        "mirror_insight",
    ),

    QUESTION_CATEGORY_EVOLUTION: (
        "report",
        "metrics",
        "identity",
        "evolution",
        "mirror_insight",
        "previous_reports",
        "comparison",
    ),

    QUESTION_CATEGORY_EDGE_PROTECTION: (
        "report",
        "metrics",
        "identity",
        "blueprint",
        "mirror_insight",
        "behavioral_signals",
        "mirror_law",
    ),

    QUESTION_CATEGORY_EDGE_REDUCERS: (
        "report",
        "metrics",
        "identity",
        "blueprint",
        "mirror_insight",
        "behavioral_signals",
        "mirror_law",
        "loss_analysis",
    ),

    QUESTION_CATEGORY_LOSS_ANALYSIS: (
        "report",
        "metrics",
        "loss_analysis",
        "daily_analysis",
        "weekly_analysis",
        "asset_breakdown",
        "symbol_breakdown",
        "side_breakdown",
        "mirror_law",
    ),

    QUESTION_CATEGORY_MIRROR_LAW: (
        "report",
        "metrics",
        "identity",
        "blueprint",
        "mirror_law",
        "evolution",
        "mirror_insight",
    ),

    QUESTION_CATEGORY_GENERAL: (
        "report",
        "metrics",
        "identity",
        "blueprint",
        "evolution",
        "mirror_insight",
        "behavioral_signals",
        "mirror_law",
        "loss_analysis",
    ),
}


EMPTY_VALUES = (
    None,
    "",
    {},
    [],
)


def _safe_dict(value: Any) -> Dict[str, Any]:
    """
    Devuelve un diccionario válido.
    """

    return value if isinstance(value, dict) else {}


def _is_present(value: Any) -> bool:
    """
    Determina si un valor contiene evidencia utilizable.
    """

    return value not in EMPTY_VALUES


def _first_present(
    source: Dict[str, Any],
    keys: Iterable[str],
) -> Any:
    """
    Devuelve el primer valor existente y no vacío entre varias claves.
    """

    for key in keys:
        if key not in source:
            continue

        value = source.get(key)

        if _is_present(value):
            return value

    return None


def _normalize_context(
    coach_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normaliza nombres alternativos para trabajar con distintas versiones
    del Coach Context sin perder compatibilidad.
    """

    source = _safe_dict(
        coach_context
    )

    normalized = dict(
        source
    )

    aliases = {
        "report": (
            "report",
            "trading_report",
            "report_summary",
        ),
        "metrics": (
            "metrics",
            "trading_metrics",
            "report_metrics",
        ),
        "identity": (
            "identity",
            "trading_identity",
        ),
        "blueprint": (
            "blueprint",
            "trading_blueprint",
        ),
        "evolution": (
            "evolution",
            "evolution_analysis",
        ),
        "mirror_insight": (
            "mirror_insight",
            "insight",
        ),
        "behavioral_signals": (
            "behavioral_signals",
            "behavior_signals",
            "signals",
        ),
        "mirror_law": (
            "mirror_law",
            "mirror_law_analysis",
        ),
        "mirror_knowledge_base": (
            "mirror_knowledge_base",
            "knowledge_base",
            "mirror_memory",
        ),
        "loss_analysis": (
            "loss_analysis",
            "losses",
        ),
        "daily_analysis": (
            "daily_analysis",
            "day_analysis",
        ),
        "weekly_analysis": (
            "weekly_analysis",
            "week_analysis",
        ),
        "asset_breakdown": (
            "asset_breakdown",
        ),
        "symbol_breakdown": (
            "symbol_breakdown",
        ),
        "side_breakdown": (
            "side_breakdown",
        ),
        "previous_reports": (
            "previous_reports",
            "historical_reports",
        ),
        "comparison": (
            "comparison",
            "report_comparison",
        ),
    }

    for canonical_key, candidate_keys in aliases.items():
        if (
            canonical_key in normalized
            and _is_present(
                normalized.get(
                    canonical_key
                )
            )
        ):
            continue

        alias_value = _first_present(
            source=source,
            keys=candidate_keys,
        )

        if alias_value is not None:
            normalized[
                canonical_key
            ] = alias_value

    metrics = _safe_dict(
        normalized.get(
            "metrics"
        )
    )

    for breakdown_key in (
        "asset_breakdown",
        "symbol_breakdown",
        "side_breakdown",
    ):
        if (
            breakdown_key in normalized
            and _is_present(
                normalized.get(
                    breakdown_key
                )
            )
        ):
            continue

        breakdown_value = metrics.get(
            breakdown_key
        )

        if _is_present(
            breakdown_value
        ):
            normalized[
                breakdown_key
            ] = breakdown_value

    knowledge_base = _safe_dict(
        normalized.get(
            "mirror_knowledge_base"
        )
    )

    if knowledge_base:
        nested_aliases = {
            "trade_evidence": (
                "trade_evidence",
            ),
            "trade_history": (
                "trade_history",
            ),
            "monthly_analysis": (
                "monthly_analysis",
            ),
            "reconstruction_quality": (
                "reconstruction_quality",
            ),
        }

        for canonical_key, candidate_keys in nested_aliases.items():
            if (
                canonical_key in normalized
                and _is_present(
                    normalized.get(
                        canonical_key
                    )
                )
            ):
                continue

            nested_value = _first_present(
                source=knowledge_base,
                keys=candidate_keys,
            )

            if nested_value is not None:
                normalized[
                    canonical_key
                ] = nested_value

    return normalized


def select_evidence(
    coach_context: Dict[str, Any],
    category: str,
) -> Dict[str, Any]:
    """
    Selecciona la evidencia relevante para una categoría.

    La Mirror Knowledge Base se conserva siempre que exista, porque es la
    memoria completa y estructurada del trader.

    El resultado conserva:
    - la categoría de la pregunta;
    - las secciones relevantes encontradas;
    - la Mirror Knowledge Base completa;
    - una lista de secciones disponibles;
    - una lista de secciones solicitadas pero ausentes;
    - metadatos de selección.

    Nunca inventa datos faltantes.
    """

    normalized_context = _normalize_context(
        coach_context
    )

    requested_sections = (
        CATEGORY_EVIDENCE_MAP.get(
            category,
            CATEGORY_EVIDENCE_MAP[
                QUESTION_CATEGORY_GENERAL
            ],
        )
    )

    selected_evidence: Dict[str, Any] = {}
    missing_sections = []

    for section_name in requested_sections:
        section_value = normalized_context.get(
            section_name
        )

        if not _is_present(
            section_value
        ):
            missing_sections.append(
                section_name
            )
            continue

        selected_evidence[
            section_name
        ] = section_value

    knowledge_base = normalized_context.get(
        "mirror_knowledge_base"
    )

    knowledge_base_used = _is_present(
        knowledge_base
    )

    if knowledge_base_used:
        selected_evidence[
            "mirror_knowledge_base"
        ] = knowledge_base

    available_sections = sorted(
        key
        for key, value in normalized_context.items()
        if _is_present(
            value
        )
    )

    return {
        "question_category": category,
        "selected_evidence": selected_evidence,
        "available_sections": available_sections,
        "missing_relevant_sections": (
            missing_sections
        ),
        "selection_metadata": {
            "requested_sections": list(
                requested_sections
            ),
            "selected_section_count": len(
                selected_evidence
            ),
            "missing_section_count": len(
                missing_sections
            ),
            "knowledge_base_available": (
                knowledge_base_used
            ),
            "knowledge_base_included": (
                knowledge_base_used
            ),
        },
    }
