# S3ID

![example workflow](https://github.com/DataDog/s3id/actions/workflows/python-package.yml/badge.svg)

S3 Object ETags are calculated with various heuristics and across various formats.  If an S3 object is downloaded and subsequently uploaded to a new path, its ETag value is not guaranteed to remain consistent unless it's upload strategy remains consistent.

S3ID is a simple library that calculates an ETag from a local file over a series of common S3 partition sizes to determine if a match exists with a corresponding S3 object ETag.

If a match is found, infomation about how to properly upload this equivalent local file to an alternate S3 location is returned to maintain consistent ETag values.

## Usage

The following examples demonstrate that a corresponding ETag match, from data at a local file path (2nd parameter), was found with the remote S3 object Etag provided (1st parameter).

Each match displays various information about how that S3 object was previously uploaded.

### Single-Part Match
```
>>> from s3id import S3ID
>>> from pathlib import Path
>>> S3ID.unpack("f1c9645dbc14efddc7d8a322685f26eb", Path("/tmp/test_10mb.txt"))
{
	'match': True, 
	'signature': '"f1c9645dbc14efddc7d8a322685f26eb"',
	'upload_strategy': 'single_part'
}
```

The corresponding remote S3 object was uploaded as a [single object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_file).

### Multi-Part Match
```
>>> from s3id import S3ID
>>> from pathlib import Path
>>> S3ID.unpack("669fdad9e309b552f1e9cf7b489c1f73-2", Path("/tmp/test_10mb.txt"))
{
	'match': True, 
	'signature': '"669fdad9e309b552f1e9cf7b489c1f73-2"',
	'partition_in_bytes': 8388608,
	'upload_strategy': 'multi_part'
}
```

The corresponding remote S3 object was uploaded as a [multi-part object](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.create_multipart_upload) with a 2 partitions of size: 8388608 bytes (8MB).

### Mismatch
```
>>> from s3id import S3ID
>>> from pathlib import Path
>>> S3ID.unpack("669fdad9e309b552f1e9cf7b489c1f73-3", Path("/tmp/test_10mb.txt"))
{
	'match': False
}
```

A corresponding ETag was not found with the local file path presented.

### Parameters:

#### `etag`
- Type: `str`
- Required: True
- Description: An ETag string for an S3 Object in various formats:
	- Single-part ETag (without a hyphen)
	- Multi-part ETag (with a hypen) which represents a composite ETag calculations of N chunks in the format (`<hash>-<number_of_chunks>`) 

#### `path`
- Type: `Path`
- Required: True
- Description: A pathlib.Path object of a local file (i.e. `Path(<path/to/local/file>)`) to compare against the previous `etag` parameters

#### `strategy`
- Type: str
- Required: False
- Default: `default`
- Description: One of the following `STRATEGY` constant values:
	- `DEFAULT`: Depending on the threshold passed, dynamically determine either `SINGLE_PART` or `MULTI_PART`
	- `SINGLE_PART`: Always calculate a single-part ETag in the format: `<hash>`
	- `MULTI_PART`: Always calculate a multi-part Etag in the format: `<hash>-<number_of_chunks>`

#### `threshold_in_bytes`
- Type: int
- Required: False
- Default: `5242880` (`5MB`)
- Description: When choosing the `DEFAULT` `strategy`, this value determines when to create a `SINGLE_PART` ETag or `MULTI_PART` composite ETag.

#### `partition_set_in_bytes`
- Type: `Set[int]`
- Required: False
- Default: `{5242880,8388608,15728640,16777216}` #5MB, 8MB, 15MB, 16MB
- Description: A list of chunk_sizes (as number of bytes) to iterate against (i.e. {`1*1024*1024`, `2*1024*1024`, ...}).  For each value provided, an ETag will be calculated against `path` and checked against parameter `etag`.

### Return Value:
- Type: `Dict[str, Union[int, str]]`
