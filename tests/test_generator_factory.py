"""
Test cases for QTI Generator Factory functionality.

This module tests the QTIGeneratorFactory and version selection used during development.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.txttoqti.generator_factory import QTIGeneratorFactory
from src.txttoqti.qti12_generator import QTI12Generator
from src.txttoqti.qti21_generator import QTI21Generator


class TestQTIGeneratorFactory(unittest.TestCase):
    """Test cases for QTI generator factory pattern."""
    
    def test_factory_creates_qti12_by_default(self):
        """Test that factory creates QTI 1.2 generator by default (university standard)."""
        generator = QTIGeneratorFactory.create_generator()
        self.assertIsInstance(generator, QTI12Generator)
    
    def test_factory_creates_qti12_explicitly(self):
        """Test factory creates QTI 1.2 generator when explicitly requested."""
        generator = QTIGeneratorFactory.create_generator('qti12')
        self.assertIsInstance(generator, QTI12Generator)
    
    def test_factory_creates_qti21_explicitly(self):
        """Test factory creates QTI 2.1 generator when explicitly requested."""
        generator = QTIGeneratorFactory.create_generator('qti21')
        self.assertIsInstance(generator, QTI21Generator)
    
    def test_factory_raises_on_invalid_version(self):
        """Test factory raises ConversionError for invalid versions."""
        from src.txttoqti.exceptions import ConversionError
        with self.assertRaises(ConversionError):
            QTIGeneratorFactory.create_generator('invalid_version')
    
    def test_factory_supported_versions(self):
        """Test factory has correct supported versions list."""
        versions = QTIGeneratorFactory.SUPPORTED_VERSIONS
        self.assertIn('qti12', versions)
        self.assertIn('qti21', versions)
        self.assertEqual(len(versions), 2)
    
    def test_factory_default_version(self):
        """Test factory default is QTI 1.2 for university compatibility."""
        default = QTIGeneratorFactory.DEFAULT_VERSION
        self.assertEqual(default, 'qti12')
        
        # Test getter method
        default_from_method = QTIGeneratorFactory.get_default_version()
        self.assertEqual(default_from_method, 'qti12')
    
    def test_convenience_function(self):
        """Test the convenience function creates generators correctly."""
        from src.txttoqti.generator_factory import create_qti_generator
        
        # Default should be QTI 1.2
        generator = create_qti_generator()
        self.assertIsInstance(generator, QTI12Generator)
        
        # Explicit QTI 2.1
        generator21 = create_qti_generator('qti21')
        self.assertIsInstance(generator21, QTI21Generator)


if __name__ == '__main__':
    unittest.main()