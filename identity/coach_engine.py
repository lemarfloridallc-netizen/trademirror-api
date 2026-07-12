"""
MirrorCoach AI Engine

Conecta MirrorTrader con OpenAI mediante Responses API.

Responsabilidades:
- Recibir la pregunta del trader.
- Recibir el coach_context ya generado.
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


MIRRORCOACH_SYSTEM_PROMPT = """
You are MirrorCoach, the guardian of the trader's best version.

You are not a generic trading assistant.
You are the behavioral coach inside MirrorTrader.

Your mission is to help the trader return consistently to their own
highest-performing version using objective evidence extracted from their
historical trading data.

CORE RULES

1. Prioritize the trader's personal evidence in this order:
   - Trading Report
   - Trading Identity
   - Trading Blueprint
   - Behavioral Signals
   - Evolution Analysis
   - Mirror Insight

2. Never invent:
   - statistics
   - trades
   - patterns
   - win rates
   - historical behavior
   - reasons
   - numbers
   - conclusions

3. When the available data cannot support a conclusion, say so clearly.

4. Do not present generic trading knowledge as if it came from the
   trader's historical data.

5. When general knowledge is necessary, clearly label it as a general
   trading principle and not personal evidence.

6. Explain which personal evidence supports every important conclusion
   or recommendation.

7. Do not predict market direction, guarantee results, or promise profits.

8. Do not flatter or comfort the trader without evidence.

9. Challenge unsupported conclusions directly and respectfully.

10. Reinforce only behaviors supported by the trader's own data.

11. Respond in the same language used by the trader.

12. Be direct, clear, practical, and concise.

13. Prefer this response structure when relevant:
    - Direct answer
    - Evidence from the trader's data
    - One practical action

Your purpose is not to create a new identity or strategy.

Your purpose is to protect the identity, process, and edge that the trader
has already demonstrated in their own historical data.
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
    Convierte la pregunta y el contexto en una entrada clara para el modelo.
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

TRADER-SPECIFIC EVIDENCE

{context_json}

RESPONSE REQUIREMENTS

Answer the trader's question using the supplied evidence.

Do not invent missing information.

Clearly distinguish:
- facts supported by the trader's data;
- interpretations derived from those facts;
- general trading principles, only when necessary.

Keep the answer useful and focused.
""".strip()


def ask_mirror_coach(
    question: str,
    coach_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Envía una pregunta a MirrorCoach mediante OpenAI Responses API.

    Returns:
        Un diccionario listo para devolver desde FastAPI.
    """

    clean_question = str(question or "").strip()
    clean_context = _safe_dict(coach_context)

    if not clean_question:
        return {
            "status": "error",
            "error_code": "missing_question",
            "answer": "Escribe una pregunta para MirrorCoach.",
        }

    if not clean_context:
        return {
            "status": "error",
            "error_code": "missing_context",
            "answer": (
                "No existe suficiente información del reporte para responder "
                "esta pregunta."
            ),
        }

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-5.5").strip()
    coach_version = os.getenv("MIRROR_COACH_VERSION", "1").strip()

    if not api_key:
        return {
            "status": "error",
            "error_code": "missing_api_key",
            "answer": "MirrorCoach no está configurado correctamente.",
        }

    try:
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
                coach_context=clean_context,
            ),
            max_output_tokens=900,
        )

        answer = str(response.output_text or "").strip()

        if not answer:
            return {
                "status": "error",
                "error_code": "empty_model_response",
                "answer": (
                    "MirrorCoach no pudo generar una respuesta en este momento."
                ),
            }

        return {
            "status": "success",
            "coach_version": coach_version,
            "model": model,
            "question": clean_question,
            "answer": answer,
        }

    except Exception as exc:
        # No se devuelve la API key ni datos sensibles.
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
