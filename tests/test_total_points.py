"""
Test cases for total points distribution functionality.

Tests the new total_points parameter that distributes quiz points evenly
across questions that use default point values.

Author: Juliho C.C.
License: MIT
"""

import unittest
from src.txttoqti.converter import TxtToQtiConverter
from src.txttoqti.parser import QuestionParser
from src.txttoqti.models import Question, QuestionType, Choice


class TestTotalPointsDistribution(unittest.TestCase):
    """Test cases for total points distribution across questions."""

    def setUp(self):
        """Set up test fixtures."""
        self.converter = TxtToQtiConverter()
        self.parser = QuestionParser()

    def test_distribute_total_points_evenly(self):
        """Test that total points are distributed evenly across default questions."""
        # Create 4 questions with default points (1.0)
        questions = [
            Question(
                id="q1",
                text="Question 1?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q1_c1", text="A", is_correct=True),
                    Choice(id="q1_c2", text="B", is_correct=False)
                ],
                points=1.0
            ),
            Question(
                id="q2",
                text="Question 2?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q2_c1", text="A", is_correct=False),
                    Choice(id="q2_c2", text="B", is_correct=True)
                ],
                points=1.0
            ),
            Question(
                id="q3",
                text="Question 3?",
                question_type=QuestionType.TRUE_FALSE,
                choices=[
                    Choice(id="q3_c1", text="True", is_correct=True),
                    Choice(id="q3_c2", text="False", is_correct=False)
                ],
                points=1.0
            ),
            Question(
                id="q4",
                text="Question 4?",
                question_type=QuestionType.TRUE_FALSE,
                choices=[
                    Choice(id="q4_c1", text="True", is_correct=False),
                    Choice(id="q4_c2", text="False", is_correct=True)
                ],
                points=1.0
            )
        ]

        # Distribute 100 points across 4 questions
        self.converter._distribute_total_points(questions, 100.0)

        # Each question should get 25 points
        for question in questions:
            self.assertEqual(question.points, 25.0, f"Question {question.id} should have 25.0 points")

        # Total should be 100
        total_points = sum(q.points for q in questions)
        self.assertEqual(total_points, 100.0)

    def test_distribute_total_points_with_custom_points(self):
        """Test that custom points are preserved and remaining points distributed."""
        # Create questions with mix of default and custom points
        questions = [
            Question(
                id="q1",
                text="Question 1?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q1_c1", text="A", is_correct=True),
                    Choice(id="q1_c2", text="B", is_correct=False)
                ],
                points=1.0  # Default - will be adjusted
            ),
            Question(
                id="q2",
                text="Question 2?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q2_c1", text="A", is_correct=False),
                    Choice(id="q2_c2", text="B", is_correct=True)
                ],
                points=30.0  # Custom - should be preserved
            ),
            Question(
                id="q3",
                text="Question 3?",
                question_type=QuestionType.TRUE_FALSE,
                choices=[
                    Choice(id="q3_c1", text="True", is_correct=True),
                    Choice(id="q3_c2", text="False", is_correct=False)
                ],
                points=1.0  # Default - will be adjusted
            )
        ]

        # Distribute 100 points total
        self.converter._distribute_total_points(questions, 100.0)

        # Custom question should keep its points
        self.assertEqual(questions[1].points, 30.0)

        # Default questions should share remaining 70 points (35 each)
        self.assertEqual(questions[0].points, 35.0)
        self.assertEqual(questions[2].points, 35.0)

        # Total should be 100
        total_points = sum(q.points for q in questions)
        self.assertEqual(total_points, 100.0)

    def test_distribute_zero_points(self):
        """Test handling of zero total points."""
        questions = [
            Question(
                id="q1",
                text="Question 1?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q1_c1", text="A", is_correct=True),
                    Choice(id="q1_c2", text="B", is_correct=False)
                ],
                points=1.0
            )
        ]

        # Should not modify anything with zero points
        original_points = questions[0].points
        self.converter._distribute_total_points(questions, 0.0)
        self.assertEqual(questions[0].points, original_points)

    def test_distribute_no_default_questions(self):
        """Test handling when all questions have custom points."""
        questions = [
            Question(
                id="q1",
                text="Question 1?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q1_c1", text="A", is_correct=True),
                    Choice(id="q1_c2", text="B", is_correct=False)
                ],
                points=25.0  # Custom
            ),
            Question(
                id="q2",
                text="Question 2?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q2_c1", text="A", is_correct=False),
                    Choice(id="q2_c2", text="B", is_correct=True)
                ],
                points=75.0  # Custom
            )
        ]

        # Should not modify any questions
        self.converter._distribute_total_points(questions, 100.0)
        self.assertEqual(questions[0].points, 25.0)
        self.assertEqual(questions[1].points, 75.0)

    def test_distribute_empty_questions_list(self):
        """Test handling of empty questions list."""
        questions = []
        # Should not raise any errors
        self.converter._distribute_total_points(questions, 100.0)
        self.assertEqual(len(questions), 0)

    def test_custom_points_exceed_total(self):
        """Test handling when custom points exceed total points."""
        questions = [
            Question(
                id="q1",
                text="Question 1?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q1_c1", text="A", is_correct=True),
                    Choice(id="q1_c2", text="B", is_correct=False)
                ],
                points=1.0  # Default
            ),
            Question(
                id="q2",
                text="Question 2?",
                question_type=QuestionType.MULTIPLE_CHOICE,
                choices=[
                    Choice(id="q2_c1", text="A", is_correct=False),
                    Choice(id="q2_c2", text="B", is_correct=True)
                ],
                points=150.0  # Custom, exceeds total
            )
        ]

        # Should handle gracefully, giving minimum points to default questions
        self.converter._distribute_total_points(questions, 100.0)
        self.assertEqual(questions[1].points, 150.0)  # Custom preserved
        self.assertGreaterEqual(questions[0].points, 0.1)  # Minimum points

    def test_integration_with_convert_file(self):
        """Test that convert_file properly uses total_points parameter."""
        # Create a test file content
        test_content = """Q1: What is 2 + 2?
A) 3
B) 4
C) 5
ANSWER: B

Q2: What is 3 + 3?
A) 5
B) 6
C) 7
ANSWER: B

Q3: What is 4 + 4?
A) 7
B) 8
C) 9
ANSWER: B
"""
        
        # Parse the content
        questions = self.parser.parse(test_content)
        
        # Verify default points
        for question in questions:
            self.assertEqual(question.points, 1.0)
        
        # Test the distribution method directly
        self.converter._distribute_total_points(questions, 90.0)
        
        # Each of the 3 questions should get 30 points
        for question in questions:
            self.assertEqual(question.points, 30.0)
        
        # Total should be 90
        total_points = sum(q.points for q in questions)
        self.assertEqual(total_points, 90.0)


if __name__ == '__main__':
    unittest.main()