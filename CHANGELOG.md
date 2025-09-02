# Changelog for txttoqti

## [0.2.0] - 2025-09-02
### Fixed
- **CRITICAL**: Resolved API mismatch bug that made the package completely unusable
- Fixed `AttributeError: 'QTIGenerator' object has no attribute 'generate'` by correcting method calls
- Fixed file extension handling in conversion process (.qti vs .xml)

### Added
- Complete QTI 2.1 XML generation functionality with proper schema compliance
- Comprehensive question validation system for all question types
- Robust error handling and informative error messages
- Backward compatibility methods to maintain API stability
- Extensive test suite covering API fixes and end-to-end scenarios

### Improved
- Enhanced QTI generator with proper XML namespace handling
- Better validation for multiple choice, true/false, and short answer questions
- Improved code coverage and testing infrastructure
- Added development dependencies for better testing experience

### Technical Details
- Replaced skeleton QTI generator implementation with full functionality
- Added proper XML document structure with minidom formatting
- Implemented comprehensive validation logic for all supported question types
- Created extensive test coverage to prevent regression of critical bugs

## [1.0.0] - 2023-10-01
### Added
- Initial release of the txttoqti package.
- Implemented core functionality for converting text-based question banks to QTI packages.
- Added command-line interface for user interaction.
- Included comprehensive validation for question formats.
- Provided utility functions for text cleaning and file validation.
- Created unit tests for core functionalities and integration tests for component interactions.

### Documentation
- Added README.md with project overview, installation instructions, and usage examples.
- Created API documentation in docs/api.md.
- Included examples of usage in docs/examples.md.
- Provided installation instructions in docs/installation.md.