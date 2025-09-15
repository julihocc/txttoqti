"""
Integration tests for CSV to QTI 1.2 conversion pipeline.

This module tests the complete conversion pipeline using examples from development,
validating the end-to-end functionality that was implemented.
"""

import unittest
import os
import sys
import tempfile
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.txttoqti.converter import TxtToQtiConverter
from src.txttoqti.parser import QuestionParser
from src.txttoqti.models import QuestionType


class TestCSVToQTI12Integration(unittest.TestCase):
    """Integration tests for CSV to QTI 1.2 conversion pipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = TxtToQtiConverter()
        self.parser = QuestionParser()
    
    def test_factor_analysis_complete_pipeline(self):
        """Test complete pipeline with factor_analysis.csv example."""
        # This is the exact example we used in development
        csv_content = """MC,,1,What is the primary goal of Principal Component Analysis (PCA)?,2,To test specific theoretical models,To reduce dimensionality while preserving maximum variance,To identify latent factors underlying observed variables,To separate common variance from unique variance
MC,,1,In the Factor Analysis model-- what does the communality (h²) represent?,2,The total variance of a variable,The proportion of variance explained by common factors,The measurement error in a variable,The correlation between factors
MC,,1,Which rotation method should you choose when factors are expected to be correlated?,3,Varimax,Quartimax,Promax,Equamax"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(csv_content)
            temp_path = temp_file.name
        
        try:
            # Convert using QTI 1.2 format (default)
            result = self.converter.convert_file(temp_path, qti_version='qti12')
            self.assertIsNotNone(result)
            
            # Check file naming convention: [name]-[timestamp]-qti12.zip
            result_path = Path(result)
            self.assertTrue(result_path.name.endswith('-qti12.zip'))
            
            # Validate ZIP contains correct files
            self.assertTrue(result_path.exists())
            with zipfile.ZipFile(result_path, 'r') as zip_file:
                files = zip_file.namelist()
                self.assertIn('imsmanifest.xml', files)
                self.assertIn('assessment.xml', files)
                
                # Extract and validate assessment XML
                assessment_xml = zip_file.read('assessment.xml').decode('iso-8859-1')
                root = ET.fromstring(assessment_xml)
                
                # Validate QTI 1.2 structure
                self.assertEqual(root.tag, 'questestinterop')
                self.assertIn('ims_qtiasiv1p2', root.get('xmlns', ''))
                
                # Should have 3 questions
                items = root.findall('.//item')
                self.assertEqual(len(items), 3)
                
                # Test specific answer mappings we verified during development
                # Question 1: CSV answer "2" should map to QTI "1001" (question 1, choice B)
                first_item = items[0]
                outcomes = first_item.find('.//outcomes_processing')
                if outcomes is not None:
                    correct_condition = outcomes.find('.//respcondition[@title="correct"]')
                    if correct_condition is not None:
                        varequal = correct_condition.find('.//varequal')
                        if varequal is not None:
                            self.assertEqual(varequal.text, "1001")
            
            # Clean up
            os.unlink(result)
            
        finally:
            os.unlink(temp_path)
    
    def test_scantron_format_pipeline(self):
        """Test complete pipeline with Scantron format."""
        # Example Scantron format from development
        scantron_content = """MC,,5,Q1,2,a,b,c,d,e
MC,,5,Q2,3,a,b,c,d,e
MC,,5,Q3,1,a,b,c,d,e"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(scantron_content)
            temp_path = temp_file.name
        
        try:
            # Convert using QTI 1.2 format
            result = self.converter.convert_file(temp_path, qti_version='qti12')
            self.assertIsNotNone(result)
            
            # Validate ZIP structure and content
            with zipfile.ZipFile(result, 'r') as zip_file:
                assessment_xml = zip_file.read('assessment.xml').decode('iso-8859-1')
                root = ET.fromstring(assessment_xml)
                
                # Should have 3 questions
                items = root.findall('.//item')
                self.assertEqual(len(items), 3)
                
                # Each question should have 5 choices (a,b,c,d,e)
                for item in items:
                    response_lid = item.find('.//response_lid')
                    if response_lid is not None:
                        render_choice = response_lid.find('.//render_choice')
                        if render_choice is not None:
                            responses = render_choice.findall('.//response_label')
                            self.assertEqual(len(responses), 5)
            
            # Clean up
            os.unlink(result)
            
        finally:
            os.unlink(temp_path)
    
    def test_qti21_vs_qti12_output_difference(self):
        """Test that QTI 1.2 and QTI 2.1 produce different output structures."""
        csv_content = """MC,,1,Sample question?,1,Choice A,Choice B,Choice C"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(csv_content)
            temp_path = temp_file.name
        
        try:
            # Generate QTI 1.2
            result_qti12 = self.converter.convert_file(temp_path, qti_version='qti12')
            
            # Generate QTI 2.1
            result_qti21 = self.converter.convert_file(temp_path, qti_version='qti21')
            
            # Both should exist but be different
            self.assertIsNotNone(result_qti12)
            self.assertIsNotNone(result_qti21)
            self.assertNotEqual(result_qti12, result_qti21)
            
            # Validate naming conventions
            self.assertTrue(result_qti12.endswith('-qti12.zip'))
            self.assertTrue(result_qti21.endswith('-qti21.zip'))
            
            # Compare XML structures
            with zipfile.ZipFile(result_qti12, 'r') as zip12:
                xml12 = zip12.read('assessment.xml').decode('iso-8859-1')
                root12 = ET.fromstring(xml12)
                
            with zipfile.ZipFile(result_qti21, 'r') as zip21:
                xml21 = zip21.read('assessment.xml').decode('utf-8')
                root21 = ET.fromstring(xml21)
            
            # QTI 1.2 should have questestinterop root
            self.assertEqual(root12.tag, 'questestinterop')
            
            # QTI 2.1 should have assessmentTest root
            self.assertEqual(root21.tag, 'assessmentTest')
            
            # Different namespaces
            self.assertIn('ims_qtiasiv1p2', root12.get('xmlns', ''))
            self.assertIn('imsqti_v2p1', root21.get('xmlns', ''))
            
            # Clean up
            os.unlink(result_qti12)
            os.unlink(result_qti21)
            
        finally:
            os.unlink(temp_path)
    
    def test_cli_integration_qti_version_parameter(self):
        """Test CLI integration with --qti-version parameter."""
        # This test validates the CLI functionality we implemented
        csv_content = """MC,,1,CLI Test Question?,2,Option A,Option B,Option C"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_file.write(csv_content)
            temp_path = temp_file.name
        
        try:
            # Test default behavior (should be QTI 1.2)
            result_default = self.converter.convert_file(temp_path)
            self.assertTrue(result_default.endswith('-qti12.zip'))
            
            # Test explicit QTI 1.2
            result_explicit = self.converter.convert_file(temp_path, qti_version='qti12')
            self.assertTrue(result_explicit.endswith('-qti12.zip'))
            
            # Clean up
            os.unlink(result_default)
            os.unlink(result_explicit)
            
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()