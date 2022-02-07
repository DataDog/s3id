import os
import unittest
from pathlib import Path
from constants import Strategy, Units
from calculator import Calculator


class TestCalculator(unittest.TestCase):

    partition_in_bytes = 8 * Units.ONE_MB
    local_directory = os.path.dirname(os.path.abspath(__file__))
    malformed_etag = "669fdad9e309b552f1e9cf7b489c1f74-2"

    def setUp(self):
        self.ten_mb_path = Path(self.local_directory + "/fixtures/test_10mb.txt")
        self.fifty_mb_path = Path(self.local_directory + "/fixtures/test_50mb.txt")

    def test_calculate_with_single_chunk_strategy_and_default_threshold(self):
        self.assertEqual(
            Calculator(self.ten_mb_path, Strategy.SINGLE_PART).calculate(
                self.partition_in_bytes
            ),
            {
                "signature": '"f1c9645dbc14efddc7d8a322685f26eb"',
                "strategy": "single_part",
            },
        )

    def test_calculate_with_multi_part_strategy_and_default_threshold(self):
        self.assertEqual(
            Calculator(self.ten_mb_path, Strategy.MULTI_PART).calculate(
                self.partition_in_bytes
            ),
            {
                "signature": '"669fdad9e309b552f1e9cf7b489c1f73-2"',
                "strategy": "multi_part",
            },
        )

    def test_calculate_with_default_strategy_and_default_threshold(self):
        self.assertEqual(
            Calculator(self.ten_mb_path, Strategy.SINGLE_PART).calculate(
                self.partition_in_bytes
            ),
            {
                "signature": '"f1c9645dbc14efddc7d8a322685f26eb"',
                "strategy": "single_part",
            },
        )

    def test_calculate_with_default_strategy_and_a_higher_threshold(self):
        self.assertEqual(
            Calculator(
                self.ten_mb_path, threshold_in_bytes=Units.ONE_MB * 50
            ).calculate(self.partition_in_bytes),
            {
                "signature": '"f1c9645dbc14efddc7d8a322685f26eb"',
                "strategy": "single_part",
            },
        )

    def test_calculate_with_default_strategy_and_a_lower_threshold(self):
        self.assertEqual(
            Calculator(
                self.fifty_mb_path, threshold_in_bytes=Units.ONE_MB * 3
            ).calculate(self.partition_in_bytes),
            {
                "signature": '"73d8a713f6f80a5e82a0ea8c92f0cab1-7"',
                "strategy": "multi_part",
            },
        )

    def test_with_an_invalid_file(self):
        with self.assertRaisesRegex(
            ValueError, "'local_file_path' must be a valid pathlib.Path object"
        ):
            Calculator("file")

    def test_with_an_invalid_mode(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid Strategy 'foo' passed. Please choose from 'single_part', 'multi_part', or 'default'",
        ):
            Calculator(self.fifty_mb_path, "foo")

    def test_with_an_invalid_threshold_in_bytes(self):
        with self.assertRaisesRegex(
            ValueError,
            "Invalid threshold_in_bytes parameter '0'. Must be a positive integer.",
        ):
            Calculator(self.fifty_mb_path, threshold_in_bytes=0)
