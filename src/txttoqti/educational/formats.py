"""
Educational Format Converter

Handles conversion between educational question formats and txttoqti-compatible format.
Supports the common educational format: Q1: A) B) C) D) RESPUESTA: X
Also supports Scantron CSV format for Canvas LMS import.

Author: Juliho C.C.
License: MIT
"""

import re
import csv
from typing import List, Tuple, Dict, Any
from pathlib import Path
from io import StringIO


class FormatConverter:
    """
    Converts between educational and txttoqti formats.
    
    Educational format:
        Q1: What is the result of type(42) in Python?
        A) <class 'float'>
        B) <class 'int'>
        C) <class 'str'>
        D) <class 'number'>
        RESPUESTA: B
    
    txttoqti format:
        1. What is the result of type(42) in Python?
        a) <class 'float'>
        b) <class 'int'>
        c) <class 'str'>
        d) <class 'number'>
        Respuesta correcta: b
    """
    
    # Conversion methods removed - parser now handles educational format directly
    
    @staticmethod
    def validate_question_format(content: str) -> Tuple[bool, List[str]]:
        """
        Validate the educational question format.
        
        Args:
            content: Text content to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        lines = content.strip().split('\n')
        
        question_pattern = re.compile(r'^Q(\d+):\s*(.+)$')
        choice_pattern = re.compile(r'^([ABCD])\)\s*(.+)$')
        answer_pattern = re.compile(r'^RESPUESTA:\s*([A-Z])$')
        
        current_question = None
        choices_for_question = []
        question_numbers = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check question format
            question_match = question_pattern.match(line)
            if question_match:
                question_num = int(question_match.group(1))
                
                # Check for duplicate question numbers
                if question_num in question_numbers:
                    errors.append(f"Line {line_num}: Duplicate question number Q{question_num}")
                else:
                    question_numbers.append(question_num)
                
                # Reset for new question
                current_question = question_num
                choices_for_question = []
                continue
            
            # Check choice format
            choice_match = choice_pattern.match(line)
            if choice_match:
                choice_letter = choice_match.group(1)
                
                if current_question is None:
                    errors.append(f"Line {line_num}: Choice found without preceding question")
                elif choice_letter in choices_for_question:
                    errors.append(f"Line {line_num}: Duplicate choice {choice_letter} for question Q{current_question}")
                else:
                    choices_for_question.append(choice_letter)
                continue
            
            # Check answer format
            answer_match = answer_pattern.match(line)
            if answer_match:
                answer_letter = answer_match.group(1)
                
                if current_question is None:
                    errors.append(f"Line {line_num}: Answer found without preceding question")
                elif answer_letter not in choices_for_question:
                    errors.append(f"Line {line_num}: Answer {answer_letter} does not match any choice for question Q{current_question}")
                continue
            
            # If no pattern matches, it might be an error
            if line:  # Non-empty line that doesn't match any pattern
                errors.append(f"Line {line_num}: Unrecognized format: '{line}'")
        
        # Check for sequential question numbering
        if question_numbers:
            expected_sequence = list(range(1, len(question_numbers) + 1))
            if sorted(question_numbers) != expected_sequence:
                errors.append("Question numbers are not sequential starting from 1")
        
        is_valid = len(errors) == 0
        return is_valid, errors


class CsvConverter:
    """
    Converter for Scantron CSV format to txttoqti educational format.
    
    Scantron CSV format (based on K-State Canvas documentation):
        Column A: Question type (MC, MR, TF)
        Column B: Empty (required but not used)
        Column C: Point value (1-100, up to 2 decimal places)
        Column D: Question text
        Column E: Correct answer (1-5 for a-e, comma-separated for multiple response)
        Columns F-J: Answer choices (a, b, c, d, e)
    """
    
    @staticmethod
    def csv_to_educational_format(csv_content: str) -> str:
        """
        Convert Scantron CSV format to educational format.
        
        Args:
            csv_content: CSV content as string
            
        Returns:
            Converted content in educational format
            
        Raises:
            ValueError: If CSV format is invalid
        """
        lines = csv_content.strip().split('\n')
        if not lines:
            raise ValueError("Empty CSV content")
        
        educational_lines = []
        question_number = 1
        
        reader = csv.reader(StringIO(csv_content))
        
        for row_num, row in enumerate(reader, 1):
            if not row or len(row) < 5:
                continue  # Skip empty or incomplete rows
                
            try:
                question_type = row[0].strip().upper()
                # row[1] is empty/not used
                point_value = row[2].strip() if len(row) > 2 else "1"
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
                raise ValueError(f"Invalid CSV format at row {row_num}: {e}")
        
        return '\n'.join(educational_lines)
    
    @staticmethod
    def is_csv_format(content: str) -> bool:
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