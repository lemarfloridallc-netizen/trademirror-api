"""
Mirror Recommendation Engine (MRE)

Generates prioritized improvement actions.

The objective is not to describe the trader.

The objective is to improve the trader.
"""

from typing import Dict, Any, List


def generate_recommendations(identity_payload: Dict[str, Any]) -> List[Dict[str, Any]]:

    recommendations = []

    scores = {

        "Patience": identity_payload.get("patience_score", 0),
        "Discipline": identity_payload.get("discipline_score", 0),
        "Risk Management": identity_payload.get("risk_management_score", 0),
        "Selection": identity_payload.get("selection_score", 0),
        "Consistency": identity_payload.get("consistency_score", 0),
        "Execution": identity_payload.get("execution_score", 0),
        "Psychology": identity_payload.get("psychology_score", 0),
        "Statistical Edge": identity_payload.get("statistical_edge_score", 0),
    }

    ordered = sorted(scores.items(), key=lambda x: x[1])

    priority = 1

    for dimension, value in ordered[:3]:

        recommendations.append({

            "priority": priority,

            "dimension": dimension,

            "current_score": value,

            "title": f"Improve {dimension}",

            "description":
                f"{dimension} currently has one of your lowest scores. Improving this area is expected to increase your overall trading edge.",

        })

        priority += 1

    return recommendations
