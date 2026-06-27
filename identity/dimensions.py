"""
Mirror Identity Engine - Dimensions

This file defines the official behavioral dimensions used by
the Mirror Identity Framework (MIF).

Each dimension is scored from 0 to 100.
"""

MIF_DIMENSIONS = {
    "patience_score": {
        "label": "Patience",
        "spanish_label": "Paciencia",
        "question": "Does the trader wait for high-quality opportunities?",
        "description": "Measures the ability to avoid impulsive entries and wait for valid setups.",
    },
    "discipline_score": {
        "label": "Discipline",
        "spanish_label": "Disciplina",
        "question": "Does the trader execute the plan without breaking rules?",
        "description": "Measures respect for stops, targets, daily limits, and operational consistency.",
    },
    "risk_management_score": {
        "label": "Risk Management",
        "spanish_label": "Gestión del Riesgo",
        "question": "Does the trader protect capital?",
        "description": "Measures drawdown control, loss management, position sizing, and capital preservation.",
    },
    "selection_score": {
        "label": "Opportunity Selection",
        "spanish_label": "Selección de Oportunidades",
        "question": "Does the trader choose the right assets, hours, and setups?",
        "description": "Measures the quality of assets, timing, and conditions where the trader performs best.",
    },
    "consistency_score": {
        "label": "Consistency",
        "spanish_label": "Consistencia",
        "question": "Does the trader repeat what works?",
        "description": "Measures stability of performance and repetition of profitable behavior.",
    },
    "adaptability_score": {
        "label": "Adaptability",
        "spanish_label": "Adaptabilidad",
        "question": "Can the trader adapt without losing structure?",
        "description": "Measures the ability to adjust to volatility, assets, and market conditions.",
    },
    "execution_score": {
        "label": "Execution",
        "spanish_label": "Ejecución",
        "question": "Does the trader execute with precision?",
        "description": "Measures entry quality, exit quality, timing, and trade duration control.",
    },
    "psychology_score": {
        "label": "Psychology",
        "spanish_label": "Fortaleza Psicológica",
        "question": "Does the trader remain stable under pressure?",
        "description": "Measures emotional control, recovery after losses, and avoidance of revenge trading.",
    },
    "statistical_edge_score": {
        "label": "Statistical Edge",
        "spanish_label": "Ventaja Estadística",
        "question": "Does the trader have a measurable edge?",
        "description": "Measures win rate, profit factor, expectancy, and sample size quality.",
    },
    "evolution_score": {
        "label": "Evolution",
        "spanish_label": "Evolución",
        "question": "Is the trader improving over time?",
        "description": "Measures improvement compared with previous reports and reduction of repeated mistakes.",
    },
}


DIMENSION_WEIGHTS = {
    "discipline_score": 0.18,
    "risk_management_score": 0.15,
    "statistical_edge_score": 0.15,
    "consistency_score": 0.12,
    "execution_score": 0.10,
    "patience_score": 0.10,
    "selection_score": 0.08,
    "psychology_score": 0.05,
    "adaptability_score": 0.04,
    "evolution_score": 0.03,
}
