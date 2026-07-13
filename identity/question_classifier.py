"""
MirrorCoach Question Classifier

Clasifica la intención de cada pregunta antes de construir
la evidencia que se enviará a OpenAI.

Este módulo:
- No llama a OpenAI.
- No modifica TradingReport.
- No modifica TradingIdentity.
- No modifica TradingBlueprint.
- No modifica Coach Context.
- No genera respuestas.
- No agrega costo de tokens.

Su única responsabilidad es identificar qué tipo de evidencia
necesita MirrorCoach para responder una pregunta.
"""

import re
import unicodedata
from typing import Any, Dict, List, Tuple


QUESTION_CATEGORY_IDENTITY_STRENGTH = "identity_strength"
QUESTION_CATEGORY_IDENTITY_WEAKNESS = "identity_weakness"
QUESTION_CATEGORY_IDENTITY_EVIDENCE = "identity_evidence"
QUESTION_CATEGORY_BLUEPRINT = "blueprint"
QUESTION_CATEGORY_EVOLUTION = "evolution"
QUESTION_CATEGORY_EDGE_PROTECTION = "edge_protection"
QUESTION_CATEGORY_EDGE_REDUCERS = "edge_reducers"
QUESTION_CATEGORY_LOSS_ANALYSIS = "loss_analysis"
QUESTION_CATEGORY_MIRROR_LAW = "mirror_law"
QUESTION_CATEGORY_GENERAL = "general"


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    QUESTION_CATEGORY_IDENTITY_STRENGTH: [
        "greatest trading strength",
        "biggest trading strength",
        "main trading strength",
        "greatest strength",
        "biggest strength",
        "main strength",
        "strongest quality",
        "what am i best at",
        "where am i strongest",
        "mayor fortaleza",
        "principal fortaleza",
        "fortaleza como trader",
        "en que soy mejor",
        "en que soy mas fuerte",
        "punto mas fuerte",
    ],

    QUESTION_CATEGORY_IDENTITY_WEAKNESS: [
        "biggest trading weakness",
        "greatest trading weakness",
        "main trading weakness",
        "biggest weakness",
        "greatest weakness",
        "main weakness",
        "weakest area",
        "where am i weakest",
        "mayor debilidad",
        "principal debilidad",
        "debilidad como trader",
        "punto mas debil",
        "en que soy mas debil",
    ],

    QUESTION_CATEGORY_IDENTITY_EVIDENCE: [
        "evidence supports my trading identity",
        "evidence supports my identity",
        "why is this my trading identity",
        "why am i classified",
        "prove my trading identity",
        "support my identity",
        "what evidence defines me",
        "que evidencia respalda mi identidad",
        "evidencia de mi identidad",
        "por que esta es mi identidad",
        "por que soy clasificado",
        "que demuestra mi identidad",
        "que datos respaldan mi identidad",
    ],

    QUESTION_CATEGORY_BLUEPRINT: [
        "trading blueprint",
        "my blueprint",
        "blueprint recommend",
        "blueprint say",
        "how should i trade",
        "how am i supposed to trade",
        "my trading process",
        "my operating rules",
        "mi blueprint",
        "que dice mi blueprint",
        "que recomienda mi blueprint",
        "como debo operar",
        "como deberia operar",
        "mi proceso de trading",
        "mis reglas de operacion",
    ],

    QUESTION_CATEGORY_EVOLUTION: [
        "am i improving",
        "am i getting better",
        "am i progressing",
        "am i evolving",
        "have i improved",
        "getting worse",
        "performance trend",
        "my evolution",
        "estoy mejorando",
        "estoy progresando",
        "estoy evolucionando",
        "he mejorado",
        "estoy empeorando",
        "mi evolucion",
        "tendencia de rendimiento",
    ],

    QUESTION_CATEGORY_EDGE_PROTECTION: [
        "protect my edge",
        "keep doing",
        "preserve my edge",
        "maintain my edge",
        "what should i continue",
        "what must not change",
        "how do i protect",
        "seguir haciendo",
        "proteger mi ventaja",
        "proteger mi edge",
        "conservar mi ventaja",
        "mantener mi edge",
        "que no debo cambiar",
        "que debo continuar haciendo",
    ],

    QUESTION_CATEGORY_EDGE_REDUCERS: [
        "reducing my trading edge",
        "hurting my edge",
        "destroying my edge",
        "weakening my edge",
        "what should i stop doing",
        "what behavior should i stop",
        "what is holding me back",
        "reduce my performance",
        "reduce my consistency",
        "reduce mi ventaja",
        "reduce mi edge",
        "destruye mi ventaja",
        "debilita mi ventaja",
        "que debo dejar de hacer",
        "que comportamiento debo detener",
        "que me esta frenando",
        "que reduce mi rendimiento",
    ],

    QUESTION_CATEGORY_LOSS_ANALYSIS: [
        "where do i lose the most money",
        "where am i losing money",
        "largest source of losses",
        "worst losing area",
        "worst day",
        "worst time",
        "worst asset",
        "worst setup",
        "largest loss",
        "biggest losses",
        "donde pierdo mas dinero",
        "en que pierdo mas",
        "mayor fuente de perdidas",
        "peor dia",
        "peor horario",
        "peor activo",
        "peor setup",
        "perdida mas grande",
        "mayores perdidas",
    ],

    QUESTION_CATEGORY_MIRROR_LAW: [
        "mirror law",
        "my trading law",
        "my best month",
        "best version",
        "non negotiables",
        "non-negotiables",
        "what worked before and after",
        "month before",
        "month after",
        "ley espejo",
        "mi ley",
        "ley del trader",
        "mejor mes",
        "mi mejor version",
        "no negociables",
        "mes anterior",
        "mes siguiente",
        "que funciono antes y despues",
    ],
}


def _normalize_text(value: Any) -> str:
    """
    Normaliza una pregunta para facilitar su clasificación.

    - Convierte a minúsculas.
    - Elimina acentos.
    - Elimina puntuación.
    - Reduce espacios repetidos.
    """

    text = str(value or "").strip().lower()

    normalized = unicodedata.normalize(
        "NFKD",
        text,
    )

    without_accents = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )

    without_punctuation = re.sub(
        r"[^a-z0-9\s-]",
        " ",
        without_accents,
    )

    compact_text = re.sub(
        r"\s+",
        " ",
        without_punctuation,
    ).strip()

    return compact_text


def _score_category(
    normalized_question: str,
    keywords: List[str],
) -> Tuple[int, List[str]]:
    """
    Calcula la coincidencia de una categoría.

    Las frases más largas reciben más peso porque normalmente
    representan una intención más específica.
    """

    score = 0
    matched_terms: List[str] = []

    for keyword in keywords:
        normalized_keyword = _normalize_text(
            keyword
        )

        if (
            normalized_keyword
            and normalized_keyword
            in normalized_question
        ):
            word_count = len(
                normalized_keyword.split()
            )

            phrase_score = max(
                word_count,
                1,
            )

            score += phrase_score
            matched_terms.append(keyword)

    return score, matched_terms


def classify_question(
    question: str,
) -> Dict[str, Any]:
    """
    Clasifica una pregunta de MirrorCoach.

    Returns:
        {
            "category": str,
            "confidence": float,
            "matched_terms": list[str],
            "normalized_question": str
        }

    La confianza representa la claridad de la coincidencia,
    no una probabilidad estadística.
    """

    normalized_question = _normalize_text(
        question
    )

    if not normalized_question:
        return {
            "category": QUESTION_CATEGORY_GENERAL,
            "confidence": 0.0,
            "matched_terms": [],
            "normalized_question": "",
        }

    category_results: List[
        Tuple[str, int, List[str]]
    ] = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        score, matched_terms = _score_category(
            normalized_question=normalized_question,
            keywords=keywords,
        )

        category_results.append(
            (
                category,
                score,
                matched_terms,
            )
        )

    category_results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    best_category, best_score, matched_terms = (
        category_results[0]
    )

    if best_score <= 0:
        return {
            "category": QUESTION_CATEGORY_GENERAL,
            "confidence": 0.25,
            "matched_terms": [],
            "normalized_question": (
                normalized_question
            ),
        }

    second_score = (
        category_results[1][1]
        if len(category_results) > 1
        else 0
    )

    score_difference = (
        best_score - second_score
    )

    if best_score >= 6 and score_difference >= 2:
        confidence = 0.95

    elif best_score >= 4:
        confidence = 0.85

    elif best_score >= 2:
        confidence = 0.70

    else:
        confidence = 0.55

    return {
        "category": best_category,
        "confidence": confidence,
        "matched_terms": matched_terms,
        "normalized_question": (
            normalized_question
        ),
    }
