"""
Automated Test Verification for Block A Practice Project
"""

import unittest
from importlib import import_module


class TestBlockAFundamentals(unittest.TestCase):
    def test_01_basic_call(self):
        mod1 = import_module("01_call_llm")
        # Ensure modules import and functions exist
        self.assertTrue(callable(mod1.run_basic_call_demo))
        self.assertTrue(callable(mod1.run_prompt_engineering_demo))

    def test_02_structured_json(self):
        mod2 = import_module("02_structured_json")
        result = mod2.run_structured_output_demo()
        self.assertIsNotNone(result)
        self.assertEqual(result.__class__.__name__, "TechConceptAnalysis")
        self.assertTrue(len(result.concept_name) > 0)
        self.assertTrue(len(result.key_components) >= 1)

    def test_03_tool_calling(self):
        mod3 = import_module("03_tool_calling")
        result = mod3.run_tool_calling_demo()
        self.assertIsNotNone(result)
        self.assertIn("auth-service", result.lower())

    def test_04_embeddings(self):
        mod4 = import_module("04_embeddings_demo")
        v1 = [1.0, 0.0]
        v2 = [1.0, 0.0]
        v3 = [0.0, 1.0]
        self.assertAlmostEqual(mod4.cosine_similarity(v1, v2), 1.0)
        self.assertAlmostEqual(mod4.cosine_similarity(v1, v3), 0.0)


if __name__ == "__main__":
    unittest.main()
