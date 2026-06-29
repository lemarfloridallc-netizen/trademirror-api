"""
Mirror Identity Engine - Behavioral Signals

This file defines the official behavioral signals used by the MIE.

Behavioral Signals are observable trading behaviors.
They feed the 10 MIF dimensions.
"""

BEHAVIORAL_SIGNALS = {
    "BS001": {
        "name": "Waits for Confirmation",
        "spanish_name": "Espera Confirmación",
        "description": "The trader waits for a valid confirmation before entering a trade.",
        "positive": True,
        "dimensions": ["patience_score", "discipline_score", "execution_score"],
    },
    "BS002": {
        "name": "Chases Price",
        "spanish_name": "Persigue el Precio",
        "description": "The trader enters late after price has already moved significantly.",
        "positive": False,
        "dimensions": ["patience_score", "execution_score", "psychology_score"],
    },
    "BS003": {
        "name": "Respects Stop Loss",
        "spanish_name": "Respeta el Stop Loss",
        "description": "The trader accepts the planned loss without extending risk.",
        "positive": True,
        "dimensions": ["discipline_score", "risk_management_score", "psychology_score"],
    },
    "BS004": {
        "name": "Moves Stop Emotionally",
        "spanish_name": "Mueve el Stop por Emoción",
        "description": "The trader changes the stop loss because of fear, hope, or pressure.",
        "positive": False,
        "dimensions": ["discipline_score", "risk_management_score", "psychology_score"],
    },
    "BS005": {
        "name": "Takes Profits Early",
        "spanish_name": "Cierra Ganancias Temprano",
        "description": "The trader exits winning trades before the planned target without valid reason.",
        "positive": False,
        "dimensions": ["execution_score", "discipline_score", "statistical_edge_score"],
    },
    "BS006": {
        "name": "Lets Winners Run",
        "spanish_name": "Deja Correr Ganadoras",
        "description": "The trader allows strong winning trades to reach or exceed the planned target.",
        "positive": True,
        "dimensions": ["execution_score", "statistical_edge_score", "consistency_score"],
    },
    "BS007": {
        "name": "Overtrades",
        "spanish_name": "Sobreopera",
        "description": "The trader takes more trades than the plan or edge supports.",
        "positive": False,
        "dimensions": ["discipline_score", "psychology_score", "risk_management_score"],
    },
    "BS008": {
        "name": "Trades in Ideal Session",
        "spanish_name": "Opera en Horario Ideal",
        "description": "The trader operates during the time window where performance is strongest.",
        "positive": True,
        "dimensions": ["selection_score", "consistency_score", "statistical_edge_score"],
    },
    "BS009": {
        "name": "Increases Risk After Loss",
        "spanish_name": "Aumenta Riesgo Después de Perder",
        "description": "The trader increases size or exposure after a losing trade.",
        "positive": False,
        "dimensions": ["risk_management_score", "psychology_score", "discipline_score"],
    },
    "BS010": {
        "name": "Consistent Position Size",
        "spanish_name": "Tamaño de Posición Consistente",
        "description": "The trader maintains consistent position sizing across similar trades.",
        "positive": True,
        "dimensions": ["risk_management_score", "discipline_score", "consistency_score"],
    },
}
