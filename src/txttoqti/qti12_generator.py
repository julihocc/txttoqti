"""
qti12_generator.py: QTI 1.2 Generator for Canvas LMS compatibility

Generates QTI 1.2 compliant XML from parsed questions, compatible with Canvas LMS
and other systems requiring the older QTI format.

Author: Juliho C.C.
License: MIT
"""

import uuid
from typing import List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from .models import Question, QuestionType
from .logging_config import get_logger


class QTI12Generator:
    """Generate QTI 1.2 compliant XML from parsed questions."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def generate_qti_xml(
        self, parsed_questions: List[Question], assessment_title: str = "Assessment"
    ) -> str:
        """
        Generate QTI 1.2 compliant XML from parsed questions.

        Args:
            parsed_questions (List[Question]): A list of parsed question objects.
            assessment_title (str): Title for the assessment.

        Returns:
            str: A string containing the QTI 1.2 XML representation.
        """
        self.logger.info(
            f"Generating QTI 1.2 XML for {len(parsed_questions)} questions"
        )

        # Create root questestinterop element
        root = Element("questestinterop")
        root.set("xmlns", "http://www.imsglobal.org/xsd/ims_qtiasiv1p2")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set(
            "xsi:schemaLocation",
            "http://www.imsglobal.org/xsd/ims_qtiasiv1p2 "
            "http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd",
        )

        # Create assessment
        assessment = SubElement(root, "assessment")
        assessment.set("ident", self._generate_assessment_id())
        assessment.set("title", assessment_title)

        # Add assessment metadata
        self._add_assessment_metadata(assessment)

        # Add section
        section = SubElement(assessment, "section")
        section.set("ident", "root_section")

        # Add questions to the section
        for i, question in enumerate(parsed_questions, 1):
            self._add_question_item(section, question, i)

        # Convert to string and format
        xml_str = tostring(root, encoding="unicode")

        # Format XML with proper declaration
        dom = minidom.parseString(xml_str)
        formatted_xml = dom.toprettyxml(indent="  ", encoding="ISO-8859-1").decode(
            "ISO-8859-1"
        )

        return formatted_xml

    def _generate_assessment_id(self) -> str:
        """Generate a unique assessment identifier."""
        return f"i{uuid.uuid4().hex}"

    def _generate_item_id(self) -> str:
        """Generate a unique item identifier."""
        return f"i{uuid.uuid4().hex}"

    def _generate_question_id(self) -> str:
        """Generate a unique question identifier."""
        return f"id{uuid.uuid4().hex}"

    def _add_assessment_metadata(self, assessment: Element) -> None:
        """Add metadata to the assessment."""
        qtimetadata = SubElement(assessment, "qtimetadata")

        # Max attempts
        field = SubElement(qtimetadata, "qtimetadatafield")
        label = SubElement(field, "fieldlabel")
        label.text = "cc_maxattempts"
        entry = SubElement(field, "fieldentry")
        entry.text = "1"

    def _add_question_item(
        self, section: Element, question: Question, question_num: int
    ) -> None:
        """Add a question item to the section."""
        # Create item element
        item = SubElement(section, "item")
        item.set("ident", self._generate_item_id())
        item.set("title", f"Question {question_num}")

        # Add item metadata
        self._add_item_metadata(item, question)

        # Add presentation (question content)
        self._add_presentation(item, question, question_num)

        # Add response processing (scoring)
        self._add_response_processing(item, question, question_num)

    def _add_item_metadata(self, item: Element, question: Question) -> None:
        """Add metadata to a question item."""
        itemmetadata = SubElement(item, "itemmetadata")
        qtimetadata = SubElement(itemmetadata, "qtimetadata")

        # Question type
        field1 = SubElement(qtimetadata, "qtimetadatafield")
        label1 = SubElement(field1, "fieldlabel")
        label1.text = "question_type"
        entry1 = SubElement(field1, "fieldentry")

        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            entry1.text = "multiple_choice_question"
        elif question.question_type == QuestionType.MULTIPLE_RESPONSE:
            entry1.text = "multiple_answers_question"
        elif question.question_type == QuestionType.TRUE_FALSE:
            entry1.text = "true_false_question"
        else:
            entry1.text = "short_answer_question"

        # Points possible
        field2 = SubElement(qtimetadata, "qtimetadatafield")
        label2 = SubElement(field2, "fieldlabel")
        label2.text = "points_possible"
        entry2 = SubElement(field2, "fieldentry")
        entry2.text = str(int(question.points))

        # Assessment question identifier
        field3 = SubElement(qtimetadata, "qtimetadatafield")
        label3 = SubElement(field3, "fieldlabel")
        label3.text = "assessment_question_identifierref"
        entry3 = SubElement(field3, "fieldentry")
        entry3.text = self._generate_question_id()

    def _add_presentation(
        self, item: Element, question: Question, question_num: int
    ) -> None:
        """Add presentation (question content) to the item."""
        presentation = SubElement(item, "presentation")

        # Add question text
        material = SubElement(presentation, "material")
        mattext = SubElement(material, "mattext")
        mattext.set("texttype", "text/html")
        mattext.text = question.text

        if question.question_type in [
            QuestionType.MULTIPLE_CHOICE,
            QuestionType.MULTIPLE_RESPONSE,
            QuestionType.TRUE_FALSE,
        ]:
            # Add response interaction
            response_lid = SubElement(presentation, "response_lid")
            response_lid.set("ident", "response1")
            # Set cardinality based on question type
            if question.question_type == QuestionType.MULTIPLE_RESPONSE:
                response_lid.set("rcardinality", "Multiple")
            else:
                response_lid.set("rcardinality", "Single")

            render_choice = SubElement(response_lid, "render_choice")

            # Add choices
            for i, choice in enumerate(question.choices):
                response_label = SubElement(render_choice, "response_label")
                # Generate choice ID in format: {question_num}00{choice_index}
                choice_id = f"{question_num}00{i}"
                response_label.set("ident", choice_id)

                choice_material = SubElement(response_label, "material")
                choice_mattext = SubElement(choice_material, "mattext")
                choice_mattext.set("texttype", "text/plain")
                choice_mattext.text = choice.text

    def _add_response_processing(
        self, item: Element, question: Question, question_num: int
    ) -> None:
        """Add response processing (scoring logic) to the item."""
        resprocessing = SubElement(item, "resprocessing")

        # Add outcomes
        outcomes = SubElement(resprocessing, "outcomes")
        decvar = SubElement(outcomes, "decvar")
        decvar.set("maxvalue", "100")
        decvar.set("minvalue", "0")
        decvar.set("varname", "SCORE")
        decvar.set("vartype", "Decimal")

        # Add response condition for correct answer
        respcondition = SubElement(resprocessing, "respcondition")
        respcondition.set("continue", "No")

        conditionvar = SubElement(respcondition, "conditionvar")

        # Find the correct answer and set the condition
        for i, choice in enumerate(question.choices):
            if choice.is_correct:
                varequal = SubElement(conditionvar, "varequal")
                varequal.set("respident", "response1")
                # Use the same ID format: {question_num}00{choice_index}
                correct_id = f"{question_num}00{i}"
                varequal.text = correct_id
                break

        # Set score for correct answer
        setvar = SubElement(respcondition, "setvar")
        setvar.set("action", "Set")
        setvar.set("varname", "SCORE")
        setvar.text = "100"

    def generate(
        self, questions: List[Question], assessment_title: str = "Assessment"
    ) -> str:
        """
        Alias for generate_qti_xml for backward compatibility.

        Args:
            questions: List of parsed question objects
            assessment_title: Title for the assessment

        Returns:
            QTI 1.2 XML string
        """
        return self.generate_qti_xml(questions, assessment_title)
