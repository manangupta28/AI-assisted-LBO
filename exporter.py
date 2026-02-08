import pandas as pd
from io import BytesIO

def convert_to_excel(user_inputs, ai_assumptions, all_results):
    output = BytesIO()
     
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        
        summary_data = []
        for case, metrics in all_results.items():
            summary_data.append({
                "Scenario": case.capitalize(),
                "IRR (%)": metrics["irr"],
                "Money Multiple (x)": metrics["money_multiple"],
                "Entry Equity": metrics["entry_equity"],
                "Exit Equity": metrics["exit_equity"]
            })
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Executive Summary", index=False)

        pd.DataFrame(user_inputs.items(), columns=["Input", "Value"]).to_excel(writer, sheet_name="Deal Inputs", index=False)

     
        flat_assumptions = []
        for key, value in ai_assumptions.items():
            if isinstance(value, dict):
                for case, val in value.items():
                    flat_assumptions.append({"Metric": key, "Case": case, "Value": str(val)})
            else:
                flat_assumptions.append({"Metric": key, "Case": "N/A", "Value": value})
        pd.DataFrame(flat_assumptions).to_excel(writer, sheet_name="AI Assumptions", index=False)

    return output.getvalue()