"""
sensitivity_analysis.py


Performs one-way sensitivity analysis on key LBO assumptions
using the base case as the anchor.
"""

from typing import Dict, List
from lbo_engine import run_lbo_case


def generate_range(center: float, step: float, n: int) -> List[float]:
    """
    Generates a symmetric range around a center value.

    Example:
    center=9, step=0.5, n=2
    → [8.0, 8.5, 9.0, 9.5, 10.0]
    """
    return [round(center + i * step, 2) for i in range(-n, n + 1)]


def sensitivity_analysis(
    user_inputs: Dict,
    base_case: Dict
) -> Dict:
    """
    Runs sensitivity analysis for key assumptions.
    """

    results = {}

    # -----------------------
    # Entry Multiple
    # -----------------------
    entry_values = generate_range(
        base_case["entry_multiple"], step=0.5, n=2
    )

    entry_sensitivity = {}
    for val in entry_values:
        modified_case = base_case.copy()
        modified_case["entry_multiple"] = val

        irr = run_lbo_case(user_inputs, modified_case)["irr"]
        entry_sensitivity[val] = irr

    results["entry_multiple"] = entry_sensitivity

    # -----------------------
    # Exit Multiple
    # -----------------------
    exit_values = generate_range(
        base_case["exit_multiple"], step=0.5, n=2
    )

    exit_sensitivity = {}
    for val in exit_values:
        modified_case = base_case.copy()
        modified_case["exit_multiple"] = val

        irr = run_lbo_case(user_inputs, modified_case)["irr"]
        exit_sensitivity[val] = irr

    results["exit_multiple"] = exit_sensitivity

    # -----------------------
    # Revenue Growth
    # -----------------------
    growth_values = generate_range(
        base_case["revenue_growth"], step=1.0, n=2
    )

    growth_sensitivity = {}
    for val in growth_values:
        modified_case = base_case.copy()
        modified_case["revenue_growth"] = val

        irr = run_lbo_case(user_inputs, modified_case)["irr"]
        growth_sensitivity[val] = irr

    results["revenue_growth"] = growth_sensitivity

    return results
