"""

Validates user-provided deal inputs coming from the frontend.

"""

from typing import Dict


def validate_user_inputs(inputs: Dict) -> None:
    """
    Performs validation on user inputs.
    Raises ValueError with clear messages if something is wrong.
    """

    required_numeric_fields = [
        "revenue",
        "ebitda",
        "depreciation_amortization",
        "capex",
        "tax_rate",
        "debt_percentage",
        "interest_rate",
        "hold_period_years",
    ]

    for field in required_numeric_fields:
        if field not in inputs:
            raise ValueError(f"Missing input: {field}")

        if not isinstance(inputs[field], (int, float)):
            raise ValueError(f"{field} must be a number")

        if inputs[field] < 0:
            raise ValueError(f"{field} cannot be negative")

    # Logical bounds
    if not (0 < inputs["tax_rate"] < 1):
        raise ValueError("Tax rate must be between 0 and 1")

    if not (0 <= inputs["debt_percentage"] <= 1):
        raise ValueError("Debt percentage must be between 0 and 1")

    if inputs["hold_period_years"] <= 0:
        raise ValueError("Hold period must be greater than 0")

    # Context fields
    if "industry" not in inputs or not inputs["industry"].strip():
        raise ValueError("Industry is required")

    if "geography" not in inputs or not inputs["geography"].strip():
        raise ValueError("Geography is required")
