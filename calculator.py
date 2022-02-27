import logging
from hashlib import md5
from pathlib import Path
from typing import List
from constants import Strategy, PACKAGE_NAME

log = logging.getLogger(f"{PACKAGE_NAME}.{__name__}")


class Calculator:
    def __init__(
        self,
        local_file_path: Path,
        strategy: str,
        threshold_in_bytes: int = Strategy.DEFAULT_THRESHOLD,
    ) -> None:
        if not local_file_path or not Path(local_file_path).is_file():
            raise ValueError("'local_file_path' must be a valid pathlib.Path object")

        self.local_file_path: Path = local_file_path
        self.local_file_size: int = local_file_path.stat().st_size
        log.info(
            f"Initialized local file at '{self.local_file_path}' with size: {self.local_file_size}"
        )

        self.strategy = strategy

        if not isinstance(threshold_in_bytes, int) or threshold_in_bytes <= 0:
            raise ValueError(
                f"Invalid threshold_in_bytes parameter '{threshold_in_bytes}'. Must be a positive integer."
            )

        self.threshold_in_bytes = threshold_in_bytes

    def calculate(self, partition_in_bytes: int):
        if not isinstance(partition_in_bytes, int) or partition_in_bytes <= 0:
            raise ValueError("'partition_in_bytes' must be an integer greater than 0")

        if self.strategy is Strategy.SINGLE_PART:
            log.debug("Forcing to SINGLE_PART calculation type")
            calculate_as_multi_part_etag = False
        elif self.strategy is Strategy.MULTI_PART:
            log.debug("Forcing to MULTI_PART calculation type")
            calculate_as_multi_part_etag = True

        return self.calculate_with_strategy(
            calculate_as_multi_part_etag, partition_in_bytes
        )

    def calculate_with_strategy(
        self, calculate_as_multi_part_etag: bool, partition_in_bytes: int
    ) -> str:
        """
        In very rare cases, S3 produces a multi-part ETag (ex: <hash>-<num>) for an object whose total size is
        below the chunk size specified.  In this case since both calculations are still valid, we must rely on
        whether a multi-part or single-part ETag was presented from the existing S3 object in order to
        calculate and match appropriately.
        """
        if calculate_as_multi_part_etag:
            log.debug("Calculating multi-part ETag")
            return {
                "signature": self._calculate_multi_part(partition_in_bytes),
                "strategy": Strategy.MULTI_PART,
            }

        log.debug("Calculating single-part ETag")
        return {
            "signature": self._calculate_single_part(),
            "strategy": Strategy.SINGLE_PART,
        }

    # Given a local file path and a chunk size (in bytes), read <chunk size>
    # bytes at a time and calculate an MD5 hash for each chunk.
    # Note: an MD5 hash is surrounded by '"' (ex: "<md5_hash>")
    def _calculate_multi_part(self, partition_in_bytes: int) -> str:
        """
        Calculate a digest of each chunk in a list.
        Build a md5 hexdigest of all chunks and format as:
          "{md5([digest1, digest2, ...])}-{number of chunks}"
        """
        checksums: List[str] = self._aggregate_checksums(partition_in_bytes)
        checksums_size: int = len(checksums)

        md5s: List[str] = md5(b"".join(m.digest() for m in checksums))
        signature: str = f'"{md5s.hexdigest()}-{checksums_size}"'
        log.debug(
            f"Multi-part signature: {signature} created with chunk size: {partition_in_bytes}"
        )
        return signature

    def _calculate_single_part(self) -> str:
        """
        Given a local file path, read 1 chunk (file size) and calculate an MD5 hash.
        Note: an MD5 hash is surrounded by '"' (ex: "<md5_hash>")
        """
        checksums: List[str] = self._aggregate_checksums(self.local_file_size)
        checksums_size: int = len(checksums)

        # In the case of no checksums, return a static md5 signature
        if checksums_size < 1:
            return f'"{md5().hexdigest()}"'

        # For a file <= the chunk size, produce an md5 of its single chunk
        signature: str = f'"{checksums[0].hexdigest()}"'
        log.debug(f"Single-part signature: {signature}")
        return signature

    def _aggregate_checksums(self, partition_in_bytes: int) -> List[str]:
        """
        Group a file into "partition_in_bytes" groups and return a list of MD5 hashes
        """
        checksums: List[str] = []
        with open(self.local_file_path, "rb") as f:
            while True:
                data: bytes = f.read(partition_in_bytes)
                if not data:
                    break
                checksums.append(md5(data))

        log.debug(f" {len(checksums)} checksum(s) found")
        return checksums
