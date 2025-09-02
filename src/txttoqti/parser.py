class QuestionParser:
    """
    QuestionParser: A class to parse text files and extract questions.

    This class is responsible for reading a text file containing questions
    and extracting them into a structured format for further processing.

    Attributes:
        questions (list): A list to store extracted questions.
    """

    def __init__(self):
        self.questions = []

    def parse(self, text):
        """
        Parse the input text and extract questions.

        Args:
            text (str): The text content to parse.

        Returns:
            list: A list of extracted questions.
        """
        lines = text.strip().splitlines()
        for line in lines:
            question = self._extract_question(line)
            if question:
                self.questions.append(question)
        return self.questions

    def _extract_question(self, line):
        """
        Extract a question from a single line of text.

        Args:
            line (str): A line of text.

        Returns:
            str or None: The extracted question or None if not valid.
        """
        # Implement logic to determine if the line is a valid question
        # For now, we assume any non-empty line is a question
        return line if line.strip() else None

    def clear_questions(self):
        """
        Clear the list of extracted questions.
        """
        self.questions = []