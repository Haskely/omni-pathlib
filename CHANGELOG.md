## v0.3.10 (2025-05-23)

### Fix

- **s3**: Improve error handling for 404 responses in S3Path.exists and add corresponding tests

## v0.3.9 (2025-04-02)

### Refactor

- Enhance type hints in BasePath and its implementations

## v0.3.8 (2025-02-28)

### Fix

- **s3**: Remove redundant headers in sign_request calls

### Refactor

- **s3**: Simplify text encoding to use default UTF-8
- Expose BasePath in package initialization

## v0.3.7 (2025-02-28)

### Fix

- **s3**: Use canonical URI in signed URL generation
- Ensure path is converted to string in path initialization

## v0.3.6 (2025-02-27)

### Fix

- **s3**: URL-encode S3 URI to handle special characters

## v0.3.5 (2025-02-27)

### Fix

- **tests**: Update event loop policy for cross-platform compatibility

## v0.3.4 (2025-02-27)

### Fix

- **tests**: Configure Windows event loop policy for async testing
- **s3**: Improve Moto server configuration for dynamic port allocation
- **s3**: Fix S3Path path scheme handling when iterdir

## v0.3.3 (2025-02-26)

### Fix

- **dependencies**: Move loguru from dev to main dependencies

## v0.3.2 (2025-02-26)

## v0.3.1 (2025-01-21)

### Fix

- **tests**: Correct assertion in test_local_path_join for handling consecutive slashes

### Refactor

- **utils**: Modularize path utilities by separating is_absolute_path and join_paths

## v0.3.0 (2025-01-21)

### Feat

- **base_path**: Enhance BasePath class with path information properties
- **parse_url**: Add URL parsing utility with PathInfo dataclass

### Refactor

- **s3**: Rename config property to kwargs in S3Path class

## v0.2.0 (2025-01-19)

### Feat

- **s3**: Refactor S3Path profile handling with improved validation and error reporting
- **s3**: Enhance bucket creation with region handling and error reporting
- **s3**: Enhance S3Path initialization with profile handling and bucket/key parsing
- Add guess_protocol utility for enhanced path protocol detection

### Fix

- **s3**: Update default profile handling in S3Path initialization
- **tests**: Improve error message for invalid S3 profile in tests

### Refactor

- **s3**: Simplify S3 credentials handling and enhance environment variable support
- **guess_protocol**: Simplify protocol extraction logic and enhance handling of paths without schemas
- **s3**: Replace logging with loguru and improve warning messages for AWS profile handling
- Move guess_protocol import to specific module

## v0.1.1 (2025-01-16)

### Fix

- **s3**: Add default profile handling for AWS credentials

## v0.1.0 (2025-01-16)

### Feat

- Enhance path protocol detection in utils
- **s3**: Add logging for missing AWS credentials and default endpoint handling
- Support Local, Http and S3 path!

### Refactor

- Change ValueError to NotImplementedError for unsupported protocols in OmniPath function

### Fix

- Fix lots of bugs

## v0.0.1 (2025-01-05)

### Feat

- Basic support for Local and Http path!
