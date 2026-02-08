"""

Uses Gemini to generate STRUCTURED assumption ranges



"""


import json
from typing import Dict

from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the JSON schema for structured output
ASSUMPTION_SCHEMA = {
    "type": "object",
    "properties": {
        "entry_multiple": {
            "type": "object",
            "description": "Entry multiple ranges for downside, base, upside cases. Realistic for industry and geography.",
            "properties": {
                "downside": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "base": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "upside": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}
            },
            "required": ["downside", "base", "upside"]
        },
        "revenue_growth": {
            "type": "object",
            "description": "Annual revenue growth rate ranges (percentages) for downside, base, upside cases.",
            "properties": {
                "downside": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "base": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "upside": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}
            },
            "required": ["downside", "base", "upside"]
        },
        "exit_multiple": {
            "type": "object",
            "description": "Exit multiple ranges for downside, base, upside cases. Generally should not exceed entry multiple.",
            "properties": {
                "downside": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "base": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                "upside": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}
            },
            "required": ["downside", "base", "upside"]
        },
        "margin_change_bps": {
            "type": "object",
            "description": "Margin change in basis points. Downside negative, base 0, upside positive.",
            "properties": {
                "downside": {"type": "number"},
                "base": {"type": "number"},
                "upside": {"type": "number"}
            },
            "required": ["downside", "base", "upside"]
        },
        "confidence": {
            "type": "string",
            "enum": ["Low", "Medium", "High"],
            "description": "Confidence in the assumptions."
        }
    },
    "required": [
        "entry_multiple",
        "revenue_growth",
        "exit_multiple",
        "margin_change_bps",
        "confidence"
    ]
}


def generate_assumptions(user_inputs: Dict) -> Dict:
    """
    Calls Gemini and returns structured assumption ranges.
    """

    system_instruction = "You are a private equity investment analyst."
    contents = build_contents(user_inputs)

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ASSUMPTION_SCHEMA
        )
    )

    try:
        assumptions = response.parsed
    except AttributeError:
        # Fallback if parsed not available; parse text as JSON
        assumptions = json.loads(response.text)

    validate_assumptions(assumptions)
    return assumptions


def build_contents(user_inputs: Dict) -> str:
    """
    Builds the contents string for the API call.
    """

    return f"""
Based on the following company context, generate reasonable
LBO assumption ranges.

Company Context:
- Industry: {user_inputs["industry"]}
- Geography: {user_inputs["geography"]}
- Revenue: {user_inputs["revenue"]}
- EBITDA: {user_inputs["ebitda"]}

Rules:
- Multiples should be realistic for the industry and geography
- Growth rates must be annual percentages
- Exit multiple should generally not exceed entry multiple
"""


def validate_assumptions(assumptions: Dict) -> None:
    """
    Basic sanity checks on AI output.
    """

    required_keys = [
        "entry_multiple",
        "revenue_growth",
        "exit_multiple",
        "margin_change_bps",
        "confidence"
    ]

    for key in required_keys:
        if key not in assumptions:
            raise ValueError(f"Missing key in assumptions: {key}")