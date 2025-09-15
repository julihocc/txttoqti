"""
generator_factory.py: Factory for QTI generator selection

Provides a factory pattern to create appropriate QTI generators based on version.
Supports QTI 1.2 and QTI 2.1 formats.

Author: Juliho C.C.
License: MIT
"""

from typing import Union, Optional
from .qti12_generator import QTI12Generator
from .qti21_generator import QTI21Generator
from .exceptions import ConversionError
from .logging_config import get_logger


class QTIGeneratorFactory:
    """Factory for creating QTI generators based on version."""
    
    SUPPORTED_VERSIONS = ['qti12', 'qti21']
    DEFAULT_VERSION = 'qti12'  # Default to QTI 1.2 for university compatibility
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    @classmethod
    def create_generator(cls, version: Optional[str] = None) -> Union[QTI12Generator, QTI21Generator]:
        """
        Create a QTI generator for the specified version.
        
        Args:
            version: QTI version ('qti12', 'qti21'). Defaults to 'qti12'.
            
        Returns:
            Appropriate QTI generator instance
            
        Raises:
            ConversionError: If version is not supported
        """
        if version is None:
            version = cls.DEFAULT_VERSION
            
        version = version.lower()
        
        if version not in cls.SUPPORTED_VERSIONS:
            raise ConversionError(
                f"Unsupported QTI version: {version}. "
                f"Supported versions: {', '.join(cls.SUPPORTED_VERSIONS)}"
            )
        
        if version == 'qti12':
            return QTI12Generator()
        elif version == 'qti21':
            return QTI21Generator()
        else:
            # This should never happen due to the validation above, but satisfy type checker
            raise ConversionError(f"Unsupported QTI version: {version}")
    
    @classmethod
    def get_supported_versions(cls) -> list:
        """Get list of supported QTI versions."""
        return cls.SUPPORTED_VERSIONS.copy()
    
    @classmethod
    def get_default_version(cls) -> str:
        """Get the default QTI version."""
        return cls.DEFAULT_VERSION
    
    @classmethod
    def is_version_supported(cls, version: str) -> bool:
        """Check if a QTI version is supported."""
        return version.lower() in cls.SUPPORTED_VERSIONS


# Convenience function for backward compatibility
def create_qti_generator(version: Optional[str] = None) -> Union[QTI12Generator, QTI21Generator]:
    """
    Create a QTI generator for the specified version.
    
    Args:
        version: QTI version ('qti12', 'qti21'). Defaults to 'qti12'.
        
    Returns:
        Appropriate QTI generator instance
    """
    return QTIGeneratorFactory.create_generator(version)