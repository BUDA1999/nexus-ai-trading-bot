import tempfile
import unittest
from pathlib import Path
from ai_review import SignalReviewer
from core import Decision
from monitoring import Event, JsonlAuditLog, summarize_pnls
from strategies import GridResearch, VisionTrendStrategy
from options_research import black_scholes

class ExtensionTests(unittest.TestCase):
    def test_vision_strategy_only_matches_trend(self):
        s = VisionTrendStrategy()
        self.assertEqual(s.propose(price=10, trend="UP", visual_signal="buy").side, "BUY")
        self.assertIsNone(s.propose(price=10, trend="DOWN", visual_signal="buy"))

    def test_grid_validation(self):
        self.assertEqual(len(GridResearch.levels(1, 2, 5)), 5)
        with self.assertRaises(ValueError): GridResearch.levels(2, 1, 5)

    def test_monitor_metrics_and_jsonl(self):
        m = summarize_pnls([2, -5, 4])
        self.assertEqual(m.net_pnl, 1)
        self.assertEqual(m.max_drawdown, 5)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "events.jsonl"
            JsonlAuditLog(p).append(Event.now("signal", {"action": "WAIT"}))
            self.assertEqual(len(p.read_text().splitlines()), 1)

    def test_ai_reviewer_fails_closed(self):
        self.assertFalse(SignalReviewer().review(Decision("WAIT", "none")).approved_for_paper)
        self.assertTrue(SignalReviewer().review(Decision("BUY", "ok", 1, .9, 1.2)).approved_for_paper)

    def test_black_scholes_put_call_parity_sanity(self):
        call = black_scholes(100, 100, 1, .05, .2, "call")
        put = black_scholes(100, 100, 1, .05, .2, "put")
        self.assertAlmostEqual(call - put, 100 - 100 * 2.718281828459045 ** (-.05), places=5)

if __name__ == "__main__": unittest.main()
