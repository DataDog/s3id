import unittest
import os
from pathlib import Path
from constants import Units
from s3id import S3ID
from calculator import Calculator


class TestS3ID(unittest.TestCase):

    partition_in_bytes = 8 * Units.ONE_MB
    local_directory = os.path.dirname(os.path.abspath(__file__))
    malformed_etag = "669fdad9e309b552f1e9cf7b489c1f74-2"

    def setUp(self):
        self.path = Path(self.local_directory + "/fixtures/test_10mb.txt")
        self.etag = Calculator(self.path).calculate(
            partition_in_bytes=self.partition_in_bytes
        )[
            "signature"
        ]  # "669fdad9e309b552f1e9cf7b489c1f73-2"

    def test_s3id_with_8mb_chunk_size(self):
        self.assertEqual(
            S3ID.unpack(self.etag, self.path),
            {
                "match": True,
                "partition_in_bytes": 8388608,
                "signature": '"669fdad9e309b552f1e9cf7b489c1f73-2"',
                "upload_strategy": "multi_part",
            },
        )

    def test_aws_s3id_mismatch_with_8mb_chunk_size(self):
        self.assertEqual(
            S3ID.unpack(self.malformed_etag, self.path),
            {"match": False},
        )
