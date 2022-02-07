import logging
from pathlib import Path
from typing import Any, Dict, Set, Union

from constants import PACKAGE_NAME
from calculator import Calculator
from s3id_result import S3IDResultMatch, S3IDResultMismatch

log = logging.getLogger(f"{PACKAGE_NAME}.{__name__}")


class Comparator(Calculator):
    @classmethod
    def run(
        cls,
        etag: str,
        local_file_path: Path,
        strategy: str,
        threshold_in_bytes: int,
        partition_set_in_bytes: Set[int],
    ) -> Dict[str, Union[int, str]]:
        """
        Iteratively create ETag values over a range of chunk sizes in hopes of matching 'etag'
        and return a summary result of a match or non-match.
        """
        result: Dict[str, Any] = Comparator(
            etag,
            local_file_path,
            strategy,
            threshold_in_bytes,
            partition_set_in_bytes,
        ).summary()
        if result["match"]:
            log.info(f"S3 object etag matched local file: '{local_file_path}'")
            return result
        else:
            log.info(
                f"S3 object etag did NOT match local file: '{local_file_path}' with any chunk sizes"
            )
            return result

    def __init__(
        self,
        etag: str,
        local_file_path: Path,
        strategy: str,
        threshold_in_bytes: int,
        partition_set_in_bytes: Set[int],
    ) -> None:
        super().__init__(local_file_path, strategy, threshold_in_bytes)

        if not etag:
            raise ValueError("'etag' cannot be blank.")

        if not isinstance(partition_set_in_bytes, set) or not all(
            isinstance(x, int) for x in partition_set_in_bytes
        ):
            raise ValueError("'partition_set_in_bytes' must be a set of integers")

        self.etag: str = etag
        self.partition_set_in_bytes = partition_set_in_bytes

    def summary(self) -> Dict[str, Union[int, str]]:
        """
        Calculate an ETag from the local file contents.  If a matching ETag has been
        found to the object_etag, return:
        { "match": True, "partition_set_in_bytes": <partition_set_in_bytes> }

        If no match is found, return: { "match": False }
        """
        for partition_in_bytes in sorted(self.partition_set_in_bytes):
            result = self.calculate(partition_in_bytes)
            signature = result["signature"]
            log.debug(
                f"Calculated ETag: {signature} with chunk size (bytes): {partition_in_bytes}"
            )
            if self.etag.replace('"', "") == signature.replace('"', ""):
                return S3IDResultMatch(
                    signature, result["strategy"], partition_in_bytes
                ).summary()

        return S3IDResultMismatch(signature).summary()
