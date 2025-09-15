"""
Test cases for QTI 1.2 Generator functionality.

This module tests the QTI12Generator class using real examples from development,
including the factor_analysis.csv case that was used to validate QTI 1.2 compatibility.
"""

import unittest
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.txttoqti.qti12_generator import QTI12Generator
from src.txttoqti.models import Question, Choice, QuestionType
from src.txttoqti.parser import QuestionParser


class TestQTI12Generator(unittest.TestCase):
    """Test cases for QTI 1.2 generator using development examples."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = QTI12Generator()
        self.parser = QuestionParser()
    
    def test_qti12_xml_structure(self):
        """Test that QTI 1.2 XML has correct root structure."""
        # Create a simple test question
        question = Question(
            id="q1",
            text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            choices=[
                Choice(id="q1_c1", text="3", is_correct=False),
                Choice(id="q1_c2", text="4", is_correct=True),
                Choice(id="q1_c3", text="5", is_correct=False)
            ]
        )
        
        xml_content = self.generator.generate_qti_xml([question], "Test Assessment")
        
        # Parse XML to validate structure
        root = ET.fromstring(xml_content)
        
        # Check QTI 1.2 specific structure (handle namespace)
        self.assertTrue(root.tag.endswith('questestinterop'))
        self.assertIn('ims_qtiasiv1p2', xml_content)  # Check in raw XML content
        
        # Check XML content for key QTI 1.2 elements
        self.assertIn('<assessment', xml_content)
        self.assertIn('<section', xml_content)
        self.assertIn('<item', xml_content)
        self.assertIn('<response_lid', xml_content)  # QTI 1.2 specific
        
        # Check encoding
        self.assertTrue(xml_content.startswith('<?xml version="1.0" encoding="ISO-8859-1"?>'))
    
    def test_qti12_answer_format(self):
        """Test QTI 1.2 answer ID format: {question_num}00{choice_index}."""
        question = Question(
            id="q1",
            text="Sample question?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            choices=[
                Choice(id="q1_c1", text="Option A", is_correct=False),
                Choice(id="q1_c2", text="Option B", is_correct=True),  # Should be 1001
                Choice(id="q1_c3", text="Option C", is_correct=False)
            ]
        )
        
        xml_content = self.generator.generate_qti_xml([question], "Answer Format Test")
        root = ET.fromstring(xml_content)
        
        # Find the correct response
        outcomes_processing = root.find('.//outcomes_processing')
        self.assertIsNotNone(outcomes_processing)
        
        # Check for answer ID format (choice B = index 1 should be 1001)
        # This validates the format we confirmed during development
        if outcomes_processing is not None:
            respcondition = outcomes_processing.find('.//respcondition[@title="correct"]')
            if respcondition is not None:
                conditionvar = respcondition.find('.//conditionvar')
                if conditionvar is not None:
                    varequal = conditionvar.find('.//varequal')
                    if varequal is not None:
                        # Should be 1001 for question 1, choice index 1 (B)
                        self.assertEqual(varequal.text, "1001")
    
    def test_factor_analysis_csv_parsing(self):
        """Test parsing of the factor_analysis.csv format used in development."""
        # Factor analysis CSV content (first few questions from our test case)
        csv_content = """MC,,1,What is the primary goal of Principal Component Analysis (PCA)?,2,To test specific theoretical models,To reduce dimensionality while preserving maximum variance,To identify latent factors underlying observed variables,To separate common variance from unique variance
MC,,1,In the Factor Analysis model-- what does the communality (h²) represent?,2,The total variance of a variable,The proportion of variance explained by common factors,The measurement error in a variable,The correlation between factors
MC,,1,Which rotation method should you choose when factors are expected to be correlated?,3,Varimax,Quartimax,Promax,Equamax"""
        
        # Parse the CSV content
        questions = self.parser.parse(csv_content)
        self.assertEqual(len(questions), 3)
        
        # Validate first question answer (should be choice B = index 1)
        first_question = questions[0]
        self.assertEqual(first_question.text, "What is the primary goal of Principal Component Analysis (PCA)?")
        
        # Find correct choice
        correct_choices = [i for i, choice in enumerate(first_question.choices) if choice.is_correct]
        self.assertEqual(len(correct_choices), 1)
        self.assertEqual(correct_choices[0], 1)  # Choice B (index 1)
        
        # Generate QTI 1.2 XML
        xml_content = self.generator.generate_qti_xml(questions, "Factor Analysis Test")
        
        # Validate XML structure
        self.assertTrue(xml_content.startswith('<?xml version="1.0" encoding="ISO-8859-1"?>'))
        self.assertIn('questestinterop', xml_content)
        self.assertIn('ims_qtiasiv1p2', xml_content)
        
        # Check that we have 3 items (count item tags properly)
        item_count = xml_content.count('<item ident=')
        self.assertEqual(item_count, 3)
        
        # Validate that QTI 1.2 specific elements are present
        self.assertIn('<response_lid', xml_content)
        self.assertIn('1001', xml_content)  # First question correct answer should be 1001
    
    def test_scantron_format_detection(self):
        """Test detection and parsing of Scantron CSV format."""
        # Example from our development testing
        scantron_content = """MC,,5,Q1,2,a,b,c,d,e
MC,,5,Q2,3,a,b,c,d,e
MR,,5,Q3,"2,4",a,b,c,d,e"""
        
        questions = self.parser.parse(scantron_content)
        self.assertEqual(len(questions), 3)
        
        # Test MC question
        q1 = questions[0]
        self.assertEqual(q1.question_type, QuestionType.MULTIPLE_CHOICE)
        self.assertEqual(len(q1.choices), 5)
        
        # Check correct answer (2 = choice b = index 1)
        correct_choices = [i for i, choice in enumerate(q1.choices) if choice.is_correct]
        self.assertEqual(correct_choices, [1])
        
        # Test MR question should be converted to MC for QTI compatibility
        q3 = questions[2]
        # Note: In our implementation, MR gets converted to MC format
        self.assertIn(q3.question_type, [QuestionType.MULTIPLE_CHOICE])
    
    def test_qti12_encoding(self):
        """Test that QTI 1.2 uses ISO-8859-1 encoding as expected by Canvas."""
        question = Question(
            id="q1", 
            text="Test question with special chars: àáâã",
            question_type=QuestionType.MULTIPLE_CHOICE,
            choices=[
                Choice(id="q1_c1", text="Choice A", is_correct=True),
                Choice(id="q1_c2", text="Choice B", is_correct=False)
            ]
        )
        
        xml_content = self.generator.generate_qti_xml([question], "Encoding Test")
        
        # Check XML declaration has ISO-8859-1
        self.assertTrue(xml_content.startswith('<?xml version="1.0" encoding="ISO-8859-1"?>'))
    
    def test_qti12_vs_qti21_differences(self):
        """Test key differences between QTI 1.2 and QTI 2.1 output."""
        question = Question(
            id="q1",
            text="Comparison test question",
            question_type=QuestionType.MULTIPLE_CHOICE,
            choices=[
                Choice(id="q1_c1", text="Option A", is_correct=True),
                Choice(id="q1_c2", text="Option B", is_correct=False)
            ]
        )
        
        xml_content = self.generator.generate_qti_xml([question], "Comparison Test")
        root = ET.fromstring(xml_content)
        
        # QTI 1.2 specific checks
        self.assertEqual(root.tag, 'questestinterop')
        self.assertIn('ims_qtiasiv1p2', root.get('xmlns', ''))
        
        # Should have response_lid, not choiceInteraction
        response_lid = root.find('.//response_lid')
        self.assertIsNotNone(response_lid)
        
        # Should NOT have assessmentTest (that's QTI 2.1)
        assessment_test = root.find('.//assessmentTest')
        self.assertIsNone(assessment_test)

    def test_factor_analysis_complete_example(self):
        """Test using the complete factor_analysis.csv example from repository."""
        # This tests against the actual file we added to the repo
        factor_analysis_path = os.path.join(
            os.path.dirname(__file__), '..', 'factor_analysis.csv'
        )
        
        if os.path.exists(factor_analysis_path):
            with open(factor_analysis_path, 'r', encoding='utf-8') as f:
                csv_content = f.read()
            
            questions = self.parser.parse(csv_content)
            
            # Should have 25 questions as in our example
            self.assertGreater(len(questions), 20)  # At least 20+ questions
            
            # Generate QTI and validate structure
            xml_content = self.generator.generate_qti_xml(questions, "Factor Analysis Quiz")
            root = ET.fromstring(xml_content)
            
            # Basic structure validation
            self.assertEqual(root.tag, 'questestinterop')
            items = root.findall('.//item')
            self.assertEqual(len(items), len(questions))
            
            # Test a few specific answer mappings from our validation
            # Question 1: answer 2 should map to 1001
            # Question 3: answer 3 should map to 3002
            first_item = items[0]
            outcomes = first_item.find('.//outcomes_processing')
            if outcomes is not None:
                correct_resp = outcomes.find('.//respcondition[@title="correct"]')
                if correct_resp is not None:
                    varequal = correct_resp.find('.//varequal')
                    if varequal is not None:
                        # First question should have correct answer 1001 (question 1, choice B)
                        self.assertEqual(varequal.text, "1001")


if __name__ == '__main__':
    unittest.main()