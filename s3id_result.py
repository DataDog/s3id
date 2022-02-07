from constants import Strategy
from typing import Any, Dict


class S3IDResult:
    def __init__(
        self, match: bool, signature: str, upload_strategy: str, partition_in_bytes: int
    ) -> None:
        self.match: bool = match
        self.signature: str = signature
        self.upload_strategy: str = upload_strategy
        self.partition_in_bytes: int = partition_in_bytes

    def summary(self):
        if not self.match:
            return {"match": False}

        output: Dict[str, Any] = {
            "match": self.match,
            "signature": self.signature,
            "upload_strategy": self.upload_strategy,
        }
        if self.upload_strategy == Strategy.MULTI_PART:
            output["partition_in_bytes"] = self.partition_in_bytes

        return output


class S3IDResultMatch(S3IDResult):
    def __init__(
        self, signature: str, upload_strategy: str, partition_in_bytes: int
    ) -> None:
        super().__init__(True, signature, upload_strategy, partition_in_bytes)


class S3IDResultMismatch(S3IDResult):
    def __init__(self, signature: str) -> None:
        super().__init__(False, None, None, None)
