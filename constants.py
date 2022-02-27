DASH = "-"
PACKAGE_NAME = "s3id"


class Units:
    """
    Utility constant for easily referencing KB, MB, and GB values
    """

    ONE_KB = 1024
    ONE_MB = ONE_KB * 1024
    ONE_GB = ONE_MB * 1024


class Strategy(object):
    """
    Each mode refers to how to calculate an ETag value
    - SINGLE_PART --> MD5 value
    - MULTI_PART --> Composite MD5 values
    - DEFAULT --> Dynamically choose from the previous modes based on a file size threshold (default is DEFAULT_THRESHOLD).
    """

    SINGLE_PART = "single_part"
    MULTI_PART = "multi_part"

    DEFAULT_THRESHOLD = 5 * Units.ONE_MB


class EtagChunkSizeSet(object):
    # 8mb - AWS default chunk size - https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html
    # 15MB - s3cmd - https://s3tools.org/kb/item13.htm#:~:text=Size%20of%20each%20chunk%20of,is%205MB%2C%20maximum%20is%205GB.
    # 16MB - https://docs.aws.amazon.com/cli/latest/topic/s3-config.html
    AWS_S3 = {8 * Units.ONE_MB, 15 * Units.ONE_MB, 16 * Units.ONE_MB}
