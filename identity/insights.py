"""
Mirror Insight Engine v2

Transforms trader metrics and identity scores into human-readable,
money-aware insights.

Purpose:
Explain the trader to the trader.
"""

from typing import Dict, Any, List, Optional


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "" or value == "--":
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "" or value == "--":
            return default
        return int(float(value))
    except Exception:
        return default


def _money(value: Any) -> str:
    amount = _safe_float(value)
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"


def _percent(value: Any) -> str:
    return f"{_safe_float(value):.1f}%"


def generate_insights(
    identity_payload: Dict[str, Any],
    metrics: Optional[Dict[str, Any]] = None
) -> List[Dict[str, str]]:
    """
    Generates prioritized MirrorTrader insights.

    Compatible with v1:
    - Can be called with only identity_payload.
    - Can also receive metrics for stronger financial insights.
    """

    insights: List[Dict[str, str]] = []
    metrics = metrics or {}

    identity = identity_payload.get("identity_name", "Trader")

    edge = _safe_float(identity_payload.get("edge_score"))
    confidence = _safe_float(identity_payload.get("confidence_score"))
    discipline = _safe_float(identity_payload.get("discipline_score"))
    psychology = _safe_float(identity_payload.get("psychology_score"))
    consistency = _safe_float(identity_payload.get("consistency_score"))
    patience = _safe_float(identity_payload.get("patience_score"))
    risk_management = _safe_float(identity_payload.get("risk_management_score"))
    execution = _safe_float(identity_payload.get("execution_score"))

    total_trades = _safe_int(metrics.get("total_trades"))
    win_rate = _safe_float(metrics.get("win_rate"))
    profit_factor = _safe_float(metrics.get("profit_factor"))
    net_pnl = _safe_float(metrics.get("net_pnl"))
    best_asset = metrics.get("best_asset") or "UNKNOWN"
    worst_asset = metrics.get("worst_asset") or "UNKNOWN"
    best_asset_pnl = _safe_float(metrics.get("best_asset_pnl"))
    worst_asset_pnl = _safe_float(metrics.get("worst_asset_pnl"))
    gross_profit = _safe_float(metrics.get("gross_profit"))
    gross_loss = _safe_float(metrics.get("gross_loss"))
    average_winner = _safe_float(metrics.get("average_winner"))
    average_loser = _safe_float(metrics.get("average_loser"))

    # 1. Asset edge insight
    if best_asset != "UNKNOWN" and best_asset_pnl > 0:
        insights.append({
            "type": "asset_edge",
            "priority": "high",
            "title": f"Your edge is strongest in {best_asset}",
            "message": (
                f"{best_asset} is currently your strongest asset, contributing "
                f"{_money(best_asset_pnl)} in realized performance. This is where "
                "your statistical edge is showing up most clearly."
            ),
            "action": f"Prioritize {best_asset} setups before expanding into other assets.",
            "impact": _money(best_asset_pnl),
        })

    # 2. Capital leak insight
    if worst_asset != "UNKNOWN" and worst_asset_pnl < 0:
        insights.append({
            "type": "capital_leak",
            "priority": "high",
            "title": f"{worst_asset} is leaking capital",
            "message": (
                f"{worst_asset} is your weakest asset in this sample, with "
                f"{_money(worst_asset_pnl)} in realized losses. This may be one "
                "of the clearest places where your capital is being drained."
            ),
            "action": f"Reduce or pause {worst_asset} trading until your rules improve there.",
            "impact": _money(worst_asset_pnl),
        })

    # 3. Profit factor warning
    if profit_factor < 1:
        insights.append({
            "type": "profit_factor_warning",
            "priority": "high",
            "title": "Your losses are still overpowering your winners",
            "message": (
                f"Your current Profit Factor is {profit_factor:.2f}. This means "
                "your winning trades are not yet strong enough to overcome your losses."
            ),
            "action": "Focus on reducing bad trades before trying to increase profits.",
            "impact": _money(net_pnl),
        })
    elif profit_factor >= 1.5:
        insights.append({
            "type": "profit_factor_strength",
            "priority": "high",
            "title": "Your process is showing positive expectancy",
            "message": (
                f"Your Profit Factor is {profit_factor:.2f}. This suggests your "
                "current trading behavior has a positive statistical foundation."
            ),
            "action": "Protect the behaviors that created this edge.",
            "impact": _money(net_pnl),
        })

    # 4. Win rate / selectivity insight
    if total_trades >= 10 and win_rate < 45:
        insights.append({
            "type": "selectivity_warning",
            "priority": "medium",
            "title": "Your trade selection needs more precision",
            "message": (
                f"Your Win Rate is {_percent(win_rate)} across {total_trades} trades. "
                "This suggests you may be entering too many low-quality setups."
            ),
            "action": "Trade fewer setups and require stronger confirmation before entry.",
            "impact": "Process improvement",
        })

    # 5. Average winner vs loser
    if average_winner > 0 and average_loser < 0:
        loss_size = abs(average_loser)

        if loss_size > average_winner:
            insights.append({
                "type": "risk_reward_leak",
                "priority": "high",
                "title": "Your average loss is larger than your average win",
                "message": (
                    f"Your average winner is {_money(average_winner)}, while your "
                    f"average loser is {_money(average_loser)}. This creates pressure "
                    "on your win rate and weakens your expectancy."
                ),
                "action": "Tighten exits on losing trades and avoid letting one loss erase multiple wins.",
                "impact": "Expectancy risk",
            })
        else:
            insights.append({
                "type": "risk_reward_strength",
                "priority": "medium",
                "title": "Your winners are strong enough to support your edge",
                "message": (
                    f"Your average winner is {_money(average_winner)} and your average "
                    f"loser is {_money(average_loser)}. This gives your strategy room "
                    "to breathe when you stay disciplined."
                ),
                "action": "Keep protecting your best setups and avoid unnecessary trades.",
                "impact": "Positive structure",
            })

    # 6. Discipline insight
    if discipline and discipline < 70:
        insights.append({
            "type": "discipline_warning",
            "priority": "high",
            "title": "Discipline is limiting your growth",
            "message": (
                "Your trading ability appears stronger than your execution discipline. "
                "This means your edge may exist, but your behavior is preventing it "
                "from fully expressing itself."
            ),
            "action": "Reduce trade frequency and only execute when your checklist is fully confirmed.",
            "impact": "Behavioral leak",
        })
    elif discipline >= 85:
        insights.append({
            "type": "discipline_strength",
            "priority": "medium",
            "title": "Discipline is becoming part of your edge",
            "message": (
                f"As a {identity}, your discipline score shows that your process is "
                "becoming more controlled. This is one of the foundations of long-term consistency."
            ),
            "action": "Keep protecting your entry criteria and avoid emotional exceptions.",
            "impact": "Behavioral edge",
        })

    # 7. Psychology insight
    if psychology and psychology < 70:
        insights.append({
            "type": "psychology_warning",
            "priority": "high",
            "title": "Emotional stability needs attention",
            "message": (
                "Your psychological score suggests emotional decisions may still be "
                "reducing your ability to express your statistical edge."
            ),
            "action": "After a losing trade, pause before re-entering. Recovery matters more than revenge.",
            "impact": "Emotional leak",
        })

    # 8. Patience insight
    if patience and patience < 70:
        insights.append({
            "type": "patience_warning",
            "priority": "medium",
            "title": "Your patience is costing you quality",
            "message": (
                "Your patience score suggests that some entries may be happening before "
                "the setup is fully confirmed."
            ),
            "action": "Wait for confirmation. A missed trade is cheaper than a forced trade.",
            "impact": "Entry quality",
        })
    elif patience >= 85:
        insights.append({
            "type": "patience_strength",
            "priority": "medium",
            "title": "Patience is becoming your competitive advantage",
            "message": (
                "Your data suggests that waiting is becoming part of your edge. "
                "This is a powerful sign because patience protects both capital and confidence."
            ),
            "action": "Do not rush your best setup. Let the market come to your plan.",
            "impact": "Execution edge",
        })

    # 9. Risk management insight
    if risk_management and risk_management < 70:
        insights.append({
            "type": "risk_management_warning",
            "priority": "high",
            "title": "Risk management is your first repair point",
            "message": (
                "Your risk management score suggests that losses may still be too large "
                "relative to your winning structure."
            ),
            "action": "Protect the downside first. A good trader survives long enough for the edge to work.",
            "impact": "Capital protection",
        })

    # 10. Consistency insight
    if consistency >= 80:
        insights.append({
            "type": "consistency_strength",
            "priority": "medium",
            "title": "Consistency is becoming visible in your behavior",
            "message": (
                "Your historical behavior shows signs of increasing consistency. "
                "This is one of the strongest foundations for compounding performance."
            ),
            "action": "Repeat the same high-quality process instead of searching for more trades.",
            "impact": "Compounding behavior",
        })

    # 11. Execution insight
    if execution and execution < 70:
        insights.append({
            "type": "execution_warning",
            "priority": "medium",
            "title": "Execution quality needs more structure",
            "message": (
                "Your execution score suggests that the way trades are entered or managed "
                "may be reducing your final results."
            ),
            "action": "Define entry, stop, and target before the trade. Do not decide inside the emotion.",
            "impact": "Execution leak",
        })

    # 12. Sample size insight
    if total_trades < 20:
        insights.append({
            "type": "sample_size_warning",
            "priority": "medium",
            "title": "Your sample size is still small",
            "message": (
                f"This analysis is based on {total_trades} trades. The insights are useful, "
                "but they will become much more reliable as your trade history grows."
            ),
            "action": "Keep collecting clean trade data before making major strategy conclusions.",
            "impact": "Confidence limitation",
        })

    # 13. Edge foundation
    if edge >= 85:
        insights.append({
            "type": "edge_strength",
            "priority": "high",
            "title": "Your statistical foundation is strong",
            "message": (
                f"Your current profile as a {identity} shows a strong statistical foundation. "
                "Your objective is not to trade more, but to protect your edge."
            ),
            "action": "Do less of what weakens your edge and more of what already works.",
            "impact": "Strategic advantage",
        })

    # Default fallback
    if not insights:
        insights.append({
            "type": "neutral",
            "priority": "medium",
            "title": "Your trading profile is forming",
            "message": (
                "MirrorTrader needs more clean trading data to identify your strongest "
                "patterns with confidence."
            ),
            "action": "Keep uploading your trading history and follow your blueprint.",
            "impact": "Data building",
        })

    priority_order = {"high": 0, "medium": 1, "low": 2}

    insights = sorted(
        insights,
        key=lambda item: priority_order.get(item.get("priority", "medium"), 1)
    )

    return insights[:7]
