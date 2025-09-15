"""
parser.py: Text parsing functionality for txttoqti package.

Handles parsing of text files containing questions in various formats
and converts them into structured Question objects.
"""

import re
from typing import List, Optional, Tuple
from .models import Question, QuestionType, Choice
from .exceptions import ParseError
from .logging_config import get_logger


class QuestionParser:
    """
    Parser for extracting questions from text files.

    Supports multiple question formats and converts them into
    structured Question objects for further processing.
    """

    def __init__(self) -> None:
        """Initialize the parser with pattern matching rules."""
        self.logger = get_logger(__name__)
        self.current_question_id = 0
        
        # Regex patterns for educational question format (Q1:, A), B), ANSWER: X)
        self.patterns = {
            'numbered_question': re.compile(r'^\s*Q(\d+):\s*(.+)$'),
            'choice': re.compile(r'^\s*([A-D])\)\s*(.+)$'),
            'correct_answer': re.compile(r'^\s*ANSWER:\s*([A-D])\s*$'),
        }

    def parse(self, text: str) -> List[Question]:
        """
        Parse the input text and extract questions.

        Args:
            text: The text content to parse

        Returns:
            List of extracted Question objects

        Raises:
            ParseError: If parsing fails
        """
        try:
            self.logger.info("Starting text parsing")
            
            # Check if input appears to be CSV format and convert if needed
            if self._is_csv_format(text):
                self.logger.info("Detected CSV format, converting to educational format")
                text = self._convert_csv_to_educational(text)
            
            lines = [line.rstrip() for line in text.split('\n')]
            questions = []
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    i += 1
                    continue
                
                # Try to parse a question
                question, lines_consumed = self._parse_question_block(lines[i:])
                if question:
                    questions.append(question)
                    i += lines_consumed
                else:
                    i += 1
            
            self.logger.info(f"Parsed {len(questions)} questions")
            return questions
            
        except Exception as e:
            raise ParseError(f"Failed to parse text: {e}")

    def _parse_question_block(self, lines: List[str]) -> Tuple[Optional[Question], int]:
        """
        Parse a block of lines that should contain a complete question in educational format.
        
        Educational format:
            Q1: What is the result of type(42) in Python?
            A) <class 'float'>
            B) <class 'int'>
            C) <class 'str'>
            D) <class 'number'>
            ANSWER: B
        
        Args:
            lines: List of lines starting from potential question
            
        Returns:
            Tuple of (Question object or None, number of lines consumed)
        """
        if not lines:
            return None, 0
        
        first_line = lines[0].strip()
        
        # Check if this looks like a numbered question (Q1:, Q2:, etc.)
        match = self.patterns['numbered_question'].match(first_line)
        if not match:
            return None, 1
        
        question_num = match.group(1)
        question_text = match.group(2).strip()
        
        if not question_text:
            return None, 1
        
        self.current_question_id += 1
        question_id = f"q_{self.current_question_id}"
        
        # Start parsing the question and its choices
        lines_consumed = 1
        choices = []
        correct_choice = None
        question_type = QuestionType.MULTIPLE_CHOICE
        
        # Look for choices and correct answer in subsequent lines
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check if this is the start of the next question
            if self.patterns['numbered_question'].match(line):
                break
            
            # Check for choice (A), B), C), D))
            choice_match = self.patterns['choice'].match(line)
            if choice_match:
                choice_letter = choice_match.group(1)  # Keep uppercase for matching
                choice_text = choice_match.group(2).strip()
                
                choices.append(Choice(
                    id=f"{question_id}_{choice_letter.lower()}",
                    text=choice_text,
                    is_correct=False
                ))
                i += 1
                lines_consumed += 1
                continue
            
            # Check for correct answer indicator (ANSWER: A)
            correct_match = self.patterns['correct_answer'].match(line)
            if correct_match:
                correct_choice = correct_match.group(1)  # Keep uppercase for matching
                i += 1
                lines_consumed += 1
                continue
            
            # If we can't parse this line, move to next
            i += 1
            lines_consumed += 1
        
        # Mark the correct choice
        if correct_choice:
            for choice in choices:
                if choice.id.endswith(f"_{correct_choice.lower()}"):
                    choice.is_correct = True
                    break
        
        # Create the question
        if not choices and question_type == QuestionType.MULTIPLE_CHOICE:
            # If no choices found, treat as short answer
            question_type = QuestionType.SHORT_ANSWER
        
        try:
            question = Question(
                id=question_id,
                text=question_text,
                question_type=question_type,
                choices=choices
            )
            
            return question, lines_consumed
            
        except ValueError as e:
            raise ParseError(f"Invalid question data: {e}", line_number=1)

    def clear_questions(self) -> None:
        """Reset the parser state."""
        self.current_question_id = 0
        self.logger.debug("Parser state cleared")
    
    def _is_csv_format(self, content: str) -> bool:
        """
        Check if content appears to be in CSV format.
        
        Args:
            content: Text content to check
            
        Returns:
            True if content appears to be CSV format
        """
        lines = content.strip().split('\n')
        if not lines:
            return False
            
        # Check first few lines for CSV patterns
        csv_indicators = 0
        for line in lines[:5]:  # Check first 5 lines
            if not line.strip():
                continue
                
            # Count commas - CSV should have multiple comma-separated fields
            if line.count(',') >= 4:  # At least 5 fields (MC,,1,Question,1,...)
                csv_indicators += 1
                
            # Check for typical Scantron patterns
            if line.upper().startswith('MC,') or line.upper().startswith('MR,') or line.upper().startswith('TF,'):
                csv_indicators += 2
        
        return csv_indicators >= 2
    
    def _convert_csv_to_educational(self, csv_content: str) -> str:
        """
        Convert Scantron CSV format to educational format.
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            Converted content in educational format
        """
        import csv
        from io import StringIO
        
        lines = csv_content.strip().split('\n')
        if not lines:
            return csv_content
        
        educational_lines = []
        question_number = 1
        
        reader = csv.reader(StringIO(csv_content))
        
        for row_num, row in enumerate(reader, 1):
            if not row or len(row) < 5:
                continue  # Skip empty or incomplete rows
                
            try:
                question_type = row[0].strip().upper()
                # row[1] is empty/not used
                question_text = row[3].strip() if len(row) > 3 else ""
                correct_answer = row[4].strip() if len(row) > 4 else "1"
                
                # Get answer choices (columns F-J, indices 5-9)
                choices = []
                for i in range(5, min(len(row), 10)):  # Max 5 choices (a-e)
                    choice_text = row[i].strip()
                    if choice_text:
                        choices.append(choice_text)
                
                if not question_text:
                    continue  # Skip rows without question text
                
                if not choices:
                    # If no choices provided, create generic ones
                    choices = ["a", "b", "c", "d", "e"][:5]
                
                # Convert to educational format
                educational_lines.append(f"Q{question_number}: {question_text}")
                
                # Add choices (A), B), C), D), E))
                for i, choice_text in enumerate(choices):
                    choice_letter = chr(ord('A') + i)
                    educational_lines.append(f"{choice_letter}) {choice_text}")
                
                # Convert correct answer from number to letter
                try:
                    if question_type == "MC":  # Multiple choice
                        correct_num = int(correct_answer)
                        if 1 <= correct_num <= len(choices):
                            correct_letter = chr(ord('A') + correct_num - 1)
                            educational_lines.append(f"ANSWER: {correct_letter}")
                        else:
                            # Default to A if invalid
                            educational_lines.append("ANSWER: A")
                    elif question_type == "TF":  # True/False
                        # For True/False: 1=True=A, 0=False=B
                        if correct_answer == "1":
                            educational_lines.append("ANSWER: A")
                        else:
                            educational_lines.append("ANSWER: B")
                    else:
                        # For other types or MR (multiple response), default to A
                        educational_lines.append("ANSWER: A")
                        
                except (ValueError, IndexError):
                    # If we can't parse the correct answer, default to A
                    educational_lines.append("ANSWER: A")
                
                educational_lines.append("")  # Blank line between questions
                question_number += 1
                
            except (IndexError, ValueError) as e:
                self.logger.warning(f"Skipping invalid CSV row {row_num}: {e}")
                continue
        
        return '\n'.join(educational_lines)