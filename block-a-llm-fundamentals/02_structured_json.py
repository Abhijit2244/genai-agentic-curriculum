"""
=============================================================================
02_structured_json.py: Structured JSON Outputs with Pydantic & Schema Enforcement
=============================================================================
Block A Core Concepts Demonstrated:
1. Structured Outputs: Constraining LLM generation to strict JSON schemas.
2. Pydantic Models: Type annotations, validation, field descriptions.
3. Reliability: Eliminating parsing errors, markdown fences (```json), and format bugs.
4. Downstream Integration: Easily feeding validated Python objects into APIs/databases.
=============================================================================
"""

import json
from typing import List
from pydantic import BaseModel, Field
from google.genai import types
from config import get_gemini_client, DEFAULT_MODEL


# Define our structured output schema using Pydantic
class TechConceptAnalysis(BaseModel):
    concept_name: str = Field(description="Name of the technical concept")
    one_sentence_definition: str = Field(description="Clear, concise one-sentence definition")
    key_components: List[str] = Field(description="3-4 critical components or sub-elements")
    difficulty_level: str = Field(description="Beginner, Intermediate, or Advanced")
    typical_latency_ms: int = Field(description="Typical API round-trip latency in milliseconds")
    production_ready: bool = Field(description="Whether this pattern is recommended for production")


def run_structured_output_demo():
    print("\n" + "=" * 65)
    print("STRUCTURED OUTPUT DEMO: Pydantic + Gemini JSON Schema")
    print("=" * 65)

    client = get_gemini_client()

    prompt = (
        "Analyze 'Retrieval-Augmented Generation (RAG)' for an engineering team."
    )
    print(f"[User Query]: '{prompt}'")
    print("[Requested Schema]: TechConceptAnalysis (Pydantic model)\n")

    # Pass the Pydantic model directly to response_schema
    # Gemini enforces strict grammar-guided decoding according to this JSON schema
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TechConceptAnalysis,
            temperature=0.1,  # Low temperature ensures adherence and consistency
        ),
    )

    raw_json = response.text.strip()
    print("[Raw JSON Returned by Gemini]:")
    print(raw_json)
    print("-" * 65)

    # Validate and parse into our Pydantic Python object
    validated_obj = TechConceptAnalysis.model_validate_json(raw_json)

    print("[Parsed Type-Safe Pydantic Object]:")
    print(f"  • Concept Name      : {validated_obj.concept_name}")
    print(f"  • Definition        : {validated_obj.one_sentence_definition}")
    print(f"  • Difficulty        : {validated_obj.difficulty_level}")
    print(f"  • Typical Latency   : {validated_obj.typical_latency_ms} ms")
    print(f"  • Production Ready  : {validated_obj.production_ready}")
    print(f"  • Key Components    :")
    for comp in validated_obj.key_components:
        print(f"      - {comp}")

    print("\n[Verification]:")
    print(f"  Type check: type(validated_obj) == {type(validated_obj).__name__}")
    print(f"  JSON re-export: {json.dumps(validated_obj.model_dump(), indent=2)}")
    print("=" * 65)
    return validated_obj


if __name__ == "__main__":
    run_structured_output_demo()
