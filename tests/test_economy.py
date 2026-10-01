import copy
from fractions import Fraction
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from economy import consume, available_order, price_fraction
from build import ROOT, validate_config


class EconomicInvariants(unittest.TestCase):
    def test_fractional_hourly_rates_survive_quarter_hour_ticks(self):
        stock, carry, total = 1000, Fraction(0), 0
        for _ in range(4):
            stock, carry, used = consume(stock, carry, 50, 900)
            total += used
        self.assertEqual((total, carry), (50, 0))

    def test_shortages_do_not_accumulate_debt(self):
        carry = Fraction(0)
        for _ in range(100):
            stock, carry, used = consume(0, carry, 600, 900)
            self.assertEqual((stock, used), (0, 0))
        stock, carry, used = consume(1000, carry, 600, 900)
        self.assertEqual(used, 150)

    def test_outstanding_deliveries_reduce_available_order(self):
        self.assertEqual(available_order(500, 2400, 1800), 100)
        self.assertEqual(available_order(500, 2400, 2500), 0)

    def test_saturation_reduces_price_within_bounds(self):
        prices = [price_fraction(s, 2400) for s in range(0, 5000)]
        self.assertTrue(all(a >= b for a, b in zip(prices, prices[1:])))
        self.assertGreaterEqual(min(prices), 0)
        self.assertLessEqual(max(prices), 1)

    def test_invalid_config_is_rejected(self):
        config = json.loads((ROOT / 'config/argon-prime.json').read_text())
        for field in ('refresh_seconds', 'consumption_seconds', 'buffer_hours'):
            bad = copy.deepcopy(config)
            bad[field] = 0
            with self.assertRaises(ValueError):
                validate_config(bad)
        bad = copy.deepcopy(config)
        bad['wares'].append(bad['wares'][0])
        with self.assertRaises(ValueError):
            validate_config(bad)


if __name__ == '__main__':
    unittest.main()
