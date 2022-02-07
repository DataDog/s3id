from pathlib import Path
from comparator import Comparator
from constants import Strategy, EtagChunkSizeSet
from typing import Set


class S3ID(Comparator):
    """
    Compare an S3 object ETag and a local file with an 8MB chunk size
    """

    @classmethod
    def unpack(
        cls,
        etag: str,
        local_file_path: Path,
        strategy: str = Strategy.DEFAULT,
        threshold_in_bytes: int = Strategy.DEFAULT_THRESHOLD,
        partition_set_in_bytes: Set[int] = EtagChunkSizeSet.AWS_S3,
    ) -> bool:
        return cls.run(
            etag,
            local_file_path,
            strategy,
            threshold_in_bytes,
            partition_set_in_bytes,
        )
