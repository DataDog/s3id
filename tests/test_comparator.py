import unittest
import os
from pathlib import Path
from constants import EtagChunkSizeSet, Strategy, Units
from comparator import Comparator
from calculator import Calculator


class TestComparator(unittest.TestCase):

    partition_in_bytes = 8 * Units.ONE_MB
    local_directory = os.path.dirname(os.path.abspath(__file__))
    malformed_etag = "669fdad9e309b552f1e9cf7b489c1f74-2"

    def setUp(self):
        self.path = Path(self.local_directory + "/fixtures/test_10mb.txt")
        self.single_part_etag = Calculator(self.path, Strategy.SINGLE_PART).calculate(
            partition_in_bytes=self.partition_in_bytes
        )[
            "signature"
        ]  # "669fdad9e309b552f1e9cf7b489c1f73-2"
        self.multi_part_etag = Calculator(self.path, Strategy.MULTI_PART).calculate(
            partition_in_bytes=self.partition_in_bytes
        )[
            "signature"
        ]  # "669fdad9e309b552f1e9cf7b489c1f73-2"

    def test_run(self):
        self.assertEqual(
            Comparator.run(
                self.multi_part_etag,
                self.path,
                Strategy.MULTI_PART,
                Strategy.DEFAULT_THRESHOLD,
                EtagChunkSizeSet.AWS_S3,
            ),
            {
                "match": True,
                "partition_in_bytes": 8388608,
                "signature": '"669fdad9e309b552f1e9cf7b489c1f73-2"',
                "upload_strategy": "multi_part",
            },
        )

    def test_run_with_a_single_part_match(self):
        self.assertEqual(
            Comparator.run(
                self.single_part_etag,
                self.path,
                Strategy.SINGLE_PART,
                Strategy.DEFAULT_THRESHOLD,
                EtagChunkSizeSet.AWS_S3,
            ),
            {
                "match": True,
                "signature": '"f1c9645dbc14efddc7d8a322685f26eb"',
                "upload_strategy": "single_part",
            },
        )

    def test_run_with_a_multi_part_match(self):
        self.assertEqual(
            Comparator.run(
                self.multi_part_etag,
                self.path,
                Strategy.MULTI_PART,
                Strategy.DEFAULT_THRESHOLD,
                EtagChunkSizeSet.AWS_S3,
            ),
            {
                "match": True,
                "partition_in_bytes": 8388608,
                "signature": '"669fdad9e309b552f1e9cf7b489c1f73-2"',
                "upload_strategy": "multi_part",
            },
        )

    def test_run_without_a_match(self):
        self.assertEqual(
            Comparator.run(
                self.malformed_etag,
                self.path,
                Strategy.MULTI_PART,
                Strategy.DEFAULT_THRESHOLD,
                EtagChunkSizeSet.AWS_S3,
            ),
            {"match": False},
        )

    def test_with_a_blank_etag(self):
        with self.assertRaisesRegex(ValueError, "'etag' cannot be blank."):
            Comparator(
                None,
                self.path,
                Strategy.MULTI_PART,
                Strategy.DEFAULT_THRESHOLD,
                EtagChunkSizeSet.AWS_S3,
            )

    def test_with_a_blank_chunk_size_set(self):
        with self.assertRaisesRegex(
            ValueError, "'partition_set_in_bytes' must be a set of integers"
        ):
            Comparator(
                self.multi_part_etag,
                self.path,
                Strategy.MULTI_PART,
                Strategy.DEFAULT_THRESHOLD,
                [],
            )

    def test_with_an_invalid_chunk_size_set(self):
        with self.assertRaisesRegex(
            ValueError, "'partition_set_in_bytes' must be a set of integers"
        ):
            Comparator(
                self.multi_part_etag,
                self.path,
                Strategy.MULTI_PART,
                Strategy.DEFAULT_THRESHOLD,
                {"a"},
            )
