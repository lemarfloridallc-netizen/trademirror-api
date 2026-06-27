"""
Mirror Identity Engine - Profiles

Master library of trader archetypes.

Each profile contains:
- Behavioral description
- Coaching message
- Target values for every MIF dimension
"""

TRADING_PROFILES = {

    "PRECISION_TRADER": {

        "identity_code": "PT-001",

        "identity_name": "Precision Trader",

        "identity_description":
            "Opera pocas veces, espera confirmaciones y obtiene ventaja mediante disciplina y precisión.",

        "coach_message":
            "Tu crecimiento no depende de operar más. Depende de proteger tu estándar.",

        "primary_strength":
            "Paciencia",

        "primary_weakness":
            "Puede dejar pasar oportunidades por exceso de confirmación.",

        "ideal_environment":
            "Mercados tendenciales con estructura clara.",

        "psychological_pattern":
            "Confía cuando existe evidencia.",

        "decision_style":
            "Analítico",

        "risk_style":
            "Conservador",

        "execution_style":
            "Confirmación",

        "motto":
            "La paciencia paga mejor que la velocidad.",

        "color":
            "#16FF6A",

        "icon":
            "target",

        "targets": {

            "patience_score":95,
            "discipline_score":95,
            "risk_management_score":90,
            "selection_score":95,
            "consistency_score":90,
            "adaptability_score":70,
            "execution_score":95,
            "psychology_score":85,
            "statistical_edge_score":90,
            "evolution_score":80

        }

    }

}
