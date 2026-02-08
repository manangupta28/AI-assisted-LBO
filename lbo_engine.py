"""

Runs a deterministic LBO calculation for a single case
(downside, base, or upside).


"""

from typing import Dict


def run_lbo_case(
    user_inputs: Dict,
    case_assumptions: Dict
) -> Dict:
    """
    Runs LBO calculations for one scenario.
    """

    # ------------------------
    # Unpack user inputs
    # ------------------------
    revenue = user_inputs["revenue"]
    ebitda = user_inputs["ebitda"]
    da = user_inputs["depreciation_amortization"]
    capex = user_inputs["capex"]
    tax_rate = user_inputs["tax_rate"]
    debt_pct = user_inputs["debt_percentage"]
    interest_rate = user_inputs["interest_rate"]
    hold_years = user_inputs["hold_period_years"]

    # ------------------------
    # Unpack case assumptions
    # ------------------------
    entry_multiple = case_assumptions["entry_multiple"]
    revenue_growth = case_assumptions["revenue_growth"] / 100
    exit_multiple = case_assumptions["exit_multiple"]
    margin_change = case_assumptions["margin_change_bps"] / 10000  # bps to decimal, annual change

    # ------------------------
    # Initial calculations
    # ------------------------
    initial_margin = ebitda / revenue if revenue > 0 else 0
    initial_da_pct = da / revenue if revenue > 0 else 0
    initial_capex_pct = capex / revenue if revenue > 0 else 0

    # ------------------------
    # Entry valuation
    # ------------------------
    entry_ev = ebitda * entry_multiple
    entry_debt = entry_ev * debt_pct
    entry_equity = entry_ev - entry_debt

    # ------------------------
    # Project cash flows
    # ------------------------
    debt = entry_debt
    current_revenue = revenue
    current_margin = initial_margin

    for _ in range(hold_years):
        # Grow revenue
        current_revenue *= (1 + revenue_growth)

        # Adjust margin annually
        current_margin += margin_change

        # Ensure margin stays reasonable (0-1)
        current_margin = max(0, min(current_margin, 1))

        # Calculate EBITDA
        current_ebitda = current_revenue * current_margin

        # Scale DA and Capex
        current_da = current_revenue * initial_da_pct
        current_capex = current_revenue * initial_capex_pct

        # Interest on beginning debt
        interest = debt * interest_rate

        # EBIT, EBT, taxes
        ebit = current_ebitda - current_da
        ebt = ebit - interest
        taxes = max(ebt, 0) * tax_rate

        # Net income
        net_income = ebt - taxes

        # Levered FCF (simplified: no NWC changes)
        fcf = net_income + current_da - current_capex

        # Use FCF to pay down debt (no increase if negative)
        debt = max(debt - fcf, 0)

    # ------------------------
    # Exit valuation
    # ------------------------
    exit_ev = current_ebitda * exit_multiple
    exit_equity = exit_ev - debt

    # ------------------------
    # Returns
    # ------------------------
    money_multiple = exit_equity / entry_equity if entry_equity > 0 else 0
    irr = (money_multiple ** (1 / hold_years)) - 1 if money_multiple > 0 else 0

    return {
        "entry_equity": entry_equity,
        "exit_equity": exit_equity,
        "money_multiple": round(money_multiple, 2),
        "irr": round(irr * 100, 2)
    }