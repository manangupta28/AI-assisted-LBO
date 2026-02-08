from inputs import get_user_inputs
from assumption_generator import generate_assumptions
from case_constructor import build_cases
from sensitivity_analysis import sensitivity_analysis

def main():
    user_inputs = get_user_inputs()
    ai_assumptions = generate_assumptions(user_inputs)
    cases = build_cases(ai_assumptions)

    base_case = cases["base"]

    sensitivities = sensitivity_analysis(user_inputs, base_case)

    print("\nSENSITIVITY ANALYSIS (BASE CASE)\n")
    for variable, table in sensitivities.items():
        print(variable.upper())
        for k, v in table.items():
            print(f"  {k}: {v}%")
        print()

if __name__ == "__main__":
    main()
