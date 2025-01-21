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
