"""
Mirror Insight Engine (MInE)

Transforms numbers into human-readable insights.

Purpose:
Explain the trader to the trader.
"""

from typing import Dict, Any, List


def generate_insights(identity_payload: Dict[str, Any]) -> List[Dict[str, str]]:

    insights = []

    edge = identity_payload.get("edge_score", 0)
    identity = identity_payload.get("identity_name", "Trader")

    if edge >= 85:
        insights.append({
            "type": "strength",
            "title": "Strong Statistical Foundation",
            "message":
                f"Your current profile ({identity}) shows a strong statistical foundation. Your objective is not to trade more, but to protect your edge."
        })

    discipline = identity_payload.get("discipline_score", 0)

    if discipline < 70:
        insights.append({
            "type": "warning",
            "title": "Discipline Is Limiting Your Growth",
            "message":
                "Your trading ability appears stronger than your execution discipline. Improving discipline will likely produce the fastest improvement."
        })

    psychology = identity_payload.get("psychology_score", 0)

    if psychology < 70:
        insights.append({
            "type": "warning",
            "title": "Emotional Stability Needs Attention",
            "message":
                "Emotional decisions are reducing your ability to fully express your statistical edge."
        })

    consistency = identity_payload.get("consistency_score", 0)

    if consistency >= 80:
        insights.append({
            "type": "strength",
            "title": "Consistency Is Becoming A Competitive Advantage",
            "message":
                "Your historical behavior shows increasing consistency. Protect this habit."
        })

    return insights
