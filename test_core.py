import unittest
from trading_bot.core import Candle, atr, classify_trend, ema, filter_signal, position_size

class CoreTests(unittest.TestCase):
    def test_ema_seed_and_values(self):
        self.assertEqual(ema([1, 2, 3, 4], 2), [None, 1.5, 2.5, 3.5])

    def test_atr_wilder(self):
        bars = [Candle(10, 12, 9, 11), Candle(11, 13, 10, 12), Candle(12, 14, 11, 13)]
        self.assertEqual(atr(bars, 2), [None, 3.0, 3.0])

    def test_trend_warms_up(self):
        self.assertEqual(classify_trend([1, 2, 3], 5), "FLAT")
        self.assertEqual(classify_trend(list(range(1, 15)), 3, 2), "UP")

    def test_filter_respects_trend_spread_and_levels(self):
        d = filter_signal("BUY", "UP", 0.01, 100, 100.001, 0.001, 0.002)
        self.assertEqual(d.action, "BUY")
        self.assertAlmostEqual(d.stop, 99.986)
        self.assertEqual(filter_signal("BUY", "DOWN", .01, 100, 100.001, .001, .002).action, "WAIT")
        self.assertEqual(filter_signal("BUY", "UP", .01, 100, 100.001, .01, .002).action, "WAIT")

    def test_position_size_limits_risk_and_rounds_down(self):
        lots = position_size(10000, .01, 100, 99, contract_size=100, lot_step=.01, max_lots=2)
        self.assertEqual(lots, 1.0)
        self.assertEqual(position_size(10000, .05, 100, 99), 0.0)

    def test_invalid_candle(self):
        with self.assertRaises(ValueError):
            Candle(10, 9, 8, 10)

if __name__ == "__main__":
    unittest.main()
