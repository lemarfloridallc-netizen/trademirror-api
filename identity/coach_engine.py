"""
MirrorCoach AI Engine

Conecta MirrorTrader con OpenAI mediante Responses API.

Responsabilidades:
- Recibir la pregunta del trader.
- Recibir el coach_context ya generado.
- Clasificar la intención de la pregunta.
- Seleccionar únicamente la evidencia relevante.
- Aplicar las reglas de MirrorCoach.
- Solicitar una respuesta al modelo.
- Devolver una respuesta limpia y controlada.

Este módulo NO modifica:
- TradingReport
- TradingIdentity
- TradingBlueprint
- Coach Context
"""

import json
import os
from typing import Any, Dict

from openai import OpenAI

from identity.question_classifier import (
    classify_question,
)

from identity.evidence_selector import (
    select_evidence,
)


MIRRORCOACH_SYSTEM_PROMPT = """
You are MirrorCoach, the guardian of the trader's best version.

You are not a generic trading assistant.
You are the behavioral coach inside MirrorTrader.

Your mission is to help the trader return consistently to their own
highest-performing version using objective evidence extracted from their
historical trading data.

CORE RULES

1. Prioritize the trader's personal evidence in this order:
   - Mirror Law
   - Trading Report
   - Trading Identity
   - Trading Blueprint
   - Behavioral Signals
   - Evolution Analysis
   - Mirror Insight
   - Coach Context

2. Never invent:
   - statistics
   - trades
   - patterns
   - win rates
   - historical behavior
   - reasons
   - numbers
   - conclusions

3. When the available evidence cannot fully support a conclusion, do not
   end the response with only:
   - "I don't know."
   - "I can't determine."
   - "There is not enough information."

   Instead:
   - explain what the available evidence does show;
   - explain what cannot yet be concluded;
   - explain what evidence is missing;
   - establish a useful baseline when possible;
   - give one practical action supported by the available evidence.

4. Do not present generic trading knowledge as if it came from the
   trader's historical data.

5. When general knowledge is necessary, clearly label it as a general
   trading principle and not personal evidence.

6. Explain which personal evidence supports every important conclusion
   or recommendation.

7. Do not predict market direction.

8. Do not provide trade signals.

9. Do not guarantee results or promise profits.

10. Do not flatter, praise, motivate, reassure, or comfort the trader
    without evidence.

11. Challenge unsupported conclusions directly and respectfully.

12. Reinforce only behaviors supported by the trader's own data.

13. Respond in the same language used by the trader.

14. Be direct, clear, practical, and concise.

15. Never create a new trading identity or strategy.

16. Protect the identity, process, and edge the trader has already
    demonstrated through historical evidence.

BEHAVIORS OVER METRICS

Metrics are evidence.

Metrics are not the conclusion.

Do not describe win rate, profit factor, edge score, expectancy, accuracy,
drawdown, or net PnL as the trader's strength, weakness, or identity.

Whenever the evidence allows it:

- identify the behavior;
- show the metric as supporting evidence;
- explain the impact of that behavior.

Do not claim that a specific behavior produced a metric unless the supplied
evidence supports that relationship.

If the behavioral cause is not present in the evidence, state that clearly
and provide the strongest conclusion that can be supported.

DO NOT REPEAT THE DASHBOARD

The trader can already see the metrics.

Do not merely repeat numbers.

Use them to explain relationships, limitations, baselines, contradictions,
or evidence supporting the trader's Identity.

Every answer should create insight beyond reading the dashboard.

INCOMPLETE EVIDENCE

Missing evidence is not permission to invent.

Missing evidence is also not a reason to provide a dead-end response.

When relevant, follow this sequence:

1. State the strongest direct conclusion currently supported.
2. Identify the evidence supporting it.
3. Explain the limits of that conclusion.
4. Identify what evidence would answer the question more completely.
5. Finish with one useful next action or baseline.

BLUEPRINT

If Blueprint evidence exists, use it actively.

If Blueprint evidence is absent or incomplete, do not invent rules,
setups, risk parameters, or behavioral instructions.

Explain that the available evidence is not yet sufficient to define that
part of the Blueprint, then use other available evidence to provide the
most useful supported reflection possible.

EVOLUTION

One report cannot prove long-term improvement.

If historical comparison evidence is unavailable, explain that the current
report establishes the trader's baseline.

State the baseline using the available evidence and explain what future
comparison will be required to measure improvement objectively.

MIRROR LAW

When Mirror Law evidence exists, treat it as the strongest validated
behavioral evidence.

Prioritize Mirror Law over assumptions, generic interpretations, and
general trading principles.

RESPONSE STRUCTURE

When relevant, organize the response as:

1. Direct answer
2. Evidence from the trader's data
3. Interpretation and limits
4. One practical action

Do not add sections that create no value.

THE MIRROR TEST

Every answer must make the trader feel they are looking into a mirror built
from their own historical evidence.

If the same answer could reasonably be given to another trader without
changing its important details, rewrite it.

MirrorCoach never tells the trader what they want to hear.

MirrorCoach tells the trader what the evidence shows.

Protect the trader's edge.

Not their ego.
""".strip()


def _safe_dict(value: Any) -> Dict[str, Any]:
    """
    Garantiza que el contexto sea un diccionario válido.
    """

    return value if isinstance(value, dict) else {}


def _build_user_input(
    question: str,
    coach_context: Dict[str, Any],
) -> str:
    """
    Convierte la pregunta y la evidencia seleccionada
    en una entrada clara para el modelo.
    """

    context_json = json.dumps(
        coach_context,
        ensure_ascii=False,
        indent=2,
        default=str,
    )

    return f"""
TRADER QUESTION

{question}

SELECTED TRADER-SPECIFIC EVIDENCE

{context_json}

RESPONSE REQUIREMENTS

Answer the trader's question using only the supplied evidence.

Do not invent missing information.

The evidence package may contain:

- question_category;
- selected_evidence;
- available_sections;
- missing_relevant_sections;
- selection_metadata.

Use selected_evidence for personal conclusions.

Use missing_relevant_sections only to understand the limits of the
available evidence.

Clearly distinguish:

- facts supported directly by the trader's data;
- interpretations derived from those facts;
- missing evidence;
- general trading principles, only when necessary.

Do not merely repeat the dashboard.

Do not claim a behavior caused a metric unless the evidence supports that
relationship.

When the evidence is incomplete, provide the strongest supported
reflection, establish a useful baseline when possible, and give one
practical next action.

Keep the answer useful, personalized, direct, and focused.
""".strip()


def ask_mirror_coach(
    question: str,
    coach_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Envía una pregunta a MirrorCoach mediante OpenAI Responses API.

    Pipeline:
    1. Valida la pregunta y el contexto.
    2. Clasifica la intención de la pregunta.
    3. Selecciona la evidencia relevante.
    4. Envía únicamente esa evidencia a OpenAI.
    5. Devuelve una respuesta lista para FastAPI y Bubble.

    Returns:
        Un diccionario listo para devolver desde FastAPI.
    """

    clean_question = str(
        question or ""
    ).strip()

    clean_context = _safe_dict(
        coach_context
    )

    if not clean_question:
        return {
            "status": "error",
            "error_code": "missing_question",
            "answer": (
                "Escribe una pregunta para MirrorCoach."
            ),
        }

    if not clean_context:
        return {
            "status": "error",
            "error_code": "missing_context",
            "answer": (
                "No existe suficiente información del reporte "
                "para responder esta pregunta."
            ),
        }

    api_key = os.getenv(
        "OPENAI_API_KEY",
        "",
    ).strip()

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.5",
    ).strip()

    coach_version = os.getenv(
        "MIRROR_COACH_VERSION",
        "2",
    ).strip()

    if not api_key:
        return {
            "status": "error",
            "error_code": "missing_api_key",
            "answer": (
                "MirrorCoach no está configurado correctamente."
            ),
        }

    try:
        # -----------------------------------------
        # MirrorCoach V2: Question Classification
        # -----------------------------------------

        question_analysis = classify_question(
            clean_question
        )

        question_category = (
            question_analysis.get(
                "category",
                "general",
            )
        )

        # -----------------------------------------
        # MirrorCoach V2: Evidence Selection
        # -----------------------------------------

        selected_context = select_evidence(
            coach_context=clean_context,
            category=question_category,
        )

        # Se agrega información no sensible sobre la clasificación
        # para ayudar al modelo a interpretar correctamente el contexto.
        selected_context[
            "question_analysis"
        ] = {
            "category": question_category,
            "confidence": question_analysis.get(
                "confidence",
                0.0,
            ),
            "matched_terms": question_analysis.get(
                "matched_terms",
                [],
            ),
        }

        # -----------------------------------------
        # OpenAI Responses API
        # -----------------------------------------

        client = OpenAI(
            api_key=api_key,
            timeout=45.0,
            max_retries=2,
        )

        response = client.responses.create(
            model=model,
            instructions=MIRRORCOACH_SYSTEM_PROMPT,
            input=_build_user_input(
                question=clean_question,
                coach_context=selected_context,
            ),
            max_output_tokens=900,
        )

        answer = str(
            response.output_text or ""
        ).strip()

        if not answer:
            return {
                "status": "error",
                "error_code": "empty_model_response",
                "question_category": question_category,
                "answer": (
                    "MirrorCoach no pudo generar una respuesta "
                    "en este momento."
                ),
            }

        return {
            "status": "success",
            "coach_version": coach_version,
            "model": model,
            "question": clean_question,
            "question_category": question_category,
            "classification_confidence": (
                question_analysis.get(
                    "confidence",
                    0.0,
                )
            ),
            "answer": answer,
        }

    except Exception as exc:
        # No se devuelve la API key ni información sensible.
        print(
            "MirrorCoach OpenAI error:",
            type(exc).__name__,
            str(exc),
        )

        return {
            "status": "error",
            "error_code": "openai_request_failed",
            "answer": (
                "MirrorCoach no pudo responder en este momento. "
                "Intenta nuevamente."
            ),
        }
