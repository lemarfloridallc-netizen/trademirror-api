"""
Mirror Law Engine

Analyzes the trader's historical behavior and transforms
the best validated period into a personal operating law.
"""

from identity.mirror_law.monthly_engine import build_monthly_metrics


__all__ = [
    "build_monthly_metrics",
]
