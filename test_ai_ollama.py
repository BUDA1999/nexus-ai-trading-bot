import json
import unittest
from ai_ollama import OllamaReviewer

class OllamaReviewTests(unittest.TestCase):
    def test_structured_review_and_deterministic_guard(self):
        def transport(payload):
            self.assertEqual(payload["format"], "json")
            return {"message": {"content": json.dumps({"summary": "Verifica o contexto.", "risks": ["Volatilidade"]})}}
        result = OllamaReviewer(transport=transport).review(signal="BUY", trend="DOWN", confidence=.8,
                                                            spread_over_limit=False, risk_percent=.5, has_stop=True)
        self.assertEqual(result.status, "REVIEW_ONLY")
        self.assertTrue(any("bloquear" in risk for risk in result.risks))

    def test_fails_closed_on_transport_error(self):
        def broken(_): raise OSError("offline")
        result = OllamaReviewer(transport=broken).review(signal="BUY", trend="UP", confidence=.8,
                                                        spread_over_limit=False, risk_percent=.5, has_stop=True)
        self.assertEqual(result.status, "UNAVAILABLE")

    def test_rejects_bad_input(self):
        result = OllamaReviewer().review(signal="SEND MONEY", trend="UP", confidence=1.5,
                                         spread_over_limit=False, risk_percent=50, has_stop=True)
        self.assertEqual(result.status, "UNAVAILABLE")

if __name__ == "__main__": unittest.main()
