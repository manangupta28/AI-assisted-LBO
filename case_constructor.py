"""

Converts AI-generated assumption ranges into deterministic
single-point assumptions for Downside, Base, and Upside cases.


"""

from typing import Dict


def midpoint(range_values):
    """
    Returns the midpoint of a [low, high] range.
    Formula: (low + high) / 2
    """
    low, high = range_values
    return (low + high) / 2


def build_cases(ai_assumptions: Dict) -> Dict:
    """
    Builds downside, base, and upside cases from AI assumption ranges.
    """

    cases = {
        "downside": {},
        "base": {},
        "upside": {}
    }

    # Entry Multiple
    cases["downside"]["entry_multiple"] = midpoint(
        ai_assumptions["entry_multiple"]["downside"]
    )
    cases["base"]["entry_multiple"] = midpoint(
        ai_assumptions["entry_multiple"]["base"]
    )
    cases["upside"]["entry_multiple"] = midpoint(
        ai_assumptions["entry_multiple"]["upside"]
    )

    # Revenue Growth
    cases["downside"]["revenue_growth"] = midpoint(
        ai_assumptions["revenue_growth"]["downside"]
    )
    cases["base"]["revenue_growth"] = midpoint(
        ai_assumptions["revenue_growth"]["base"]
    )
    cases["upside"]["revenue_growth"] = midpoint(
        ai_assumptions["revenue_growth"]["upside"]
    )

    # Exit Multiple
    cases["downside"]["exit_multiple"] = midpoint(
        ai_assumptions["exit_multiple"]["downside"]
    )
    cases["base"]["exit_multiple"] = midpoint(
        ai_assumptions["exit_multiple"]["base"]
    )
    cases["upside"]["exit_multiple"] = midpoint(
        ai_assumptions["exit_multiple"]["upside"]
    )

    # Margin Change (bps) – already single values
    cases["downside"]["margin_change_bps"] = ai_assumptions["margin_change_bps"]["downside"]
    cases["base"]["margin_change_bps"] = ai_assumptions["margin_change_bps"]["base"]
    cases["upside"]["margin_change_bps"] = ai_assumptions["margin_change_bps"]["upside"]

    return cases
