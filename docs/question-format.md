# Question Format Specification

This document describes the supported question formats for the `txttoqti` package. The converter supports multiple question types and formats to accommodate different educational needs.

## Supported Question Types

### 1. Multiple Choice Questions

#### Standard Format (Educational CLI)

```
Q1: What is the result of type(42) in Python?
A) <class 'float'>
B) <class 'int'>
C) <class 'str'>
D) <class 'number'>
RESPUESTA: B
```

#### Alternative Format (Basic CLI)

```
1. ¿Cuál es la capital de México?
   - a) Guadalajara
   - b) Monterrey
   - c) Ciudad de México
   - d) Cancún
   - Respuesta correcta: c
```

### 2. True/False Questions

```
3. El océano Atlántico es el océano más grande del mundo.
   - a) Verdadero
   - b) Falso
   - Respuesta correcta: b
```

Or using the educational format:

```
Q3: Python is a compiled language.
A) True
B) False
RESPUESTA: B
```

### 3. Short Answer Questions

```
5. Nombra un país que tenga el español como idioma oficial.
   - Respuesta correcta: [Respuesta abierta]
```

```
6. ¿Cuál es el símbolo químico del agua?
   - Respuesta correcta: H2O
```

### 4. Essay Questions

```
8. Explica la importancia de la fotosíntesis en las plantas.
   - Respuesta correcta: [Respuesta abierta]
```

## Format Rules and Guidelines

### Question Numbering

- **Standard format**: Questions must start with `Q` followed by a number and colon: `Q1:`, `Q2:`, etc.
- **Alternative format**: Questions can start with a number and period: `1.`, `2.`, etc.
- Questions should be numbered sequentially

### Answer Options

#### Multiple Choice Options

- **Standard format**: Use capital letters with parentheses: `A)`, `B)`, `C)`, `D)`
- **Alternative format**: Use lowercase letters with dashes: `- a)`, `- b)`, `- c)`, `- d)`
- Each option should be on a separate line
- Options should be indented consistently

#### Correct Answer Indication

- **Standard format**: Use `RESPUESTA: [LETTER]` (e.g., `RESPUESTA: B`)
- **Alternative format**: Use `Respuesta correcta: [letter]` (e.g., `Respuesta correcta: c`)
- The correct answer indicator should be on its own line
- Case sensitivity: Match the format used in options (uppercase vs lowercase)

### Text Formatting

#### Encoding
- Use UTF-8 encoding for all text files
- Support for international characters (accents, special symbols, etc.)

#### Line Breaks
- Each question should be separated by at least one blank line
- Options should immediately follow the question text
- The correct answer should immediately follow the options

#### Whitespace
- Consistent indentation for readability (recommended: 3 spaces for alternative format)
- No trailing whitespace on lines

## Advanced Features

### Question with Code Blocks

```
Q4: What does the following code print? print("Hello" + "World")
A) Hello World
B) HelloWorld
C) Hello+World
D) Error
RESPUESTA: B
```

### Questions with Special Characters

```
Q6: What is the correct way to create a dictionary in Python?
A) dict = []
B) dict = {}
C) dict = ()
D) dict = ""
RESPUESTA: B
```

### Questions with Mathematical Expressions

```
Q9: Which operator is used for exponentiation in Python?
A) ^
B) **
C) *
D) exp()
RESPUESTA: B
```

## File Structure Requirements

### File Naming
- Recommended: `questions.txt`, `sample_questions.txt`
- Educational format: `preguntas-bloque-[NUMBER].txt` or `questions-block-[NUMBER].txt`

### File Organization
- One question bank per file
- Questions should be ordered sequentially
- Include a header comment describing the content (optional)

### Example File Header
```
# Sample Questions for txttoqti Converter
# Course: Introduction to Python Programming
# Block: 1 - Data Types and Variables

Q1: What is the result of type(42) in Python?
A) <class 'float'>
B) <class 'int'>
C) <class 'str'>
D) <class 'number'>
RESPUESTA: B
```

## Validation and Error Handling

### Common Format Errors

1. **Missing question number**: Questions must be properly numbered
2. **Incorrect answer format**: Answer indicators must match the expected pattern
3. **Missing options**: Multiple choice questions need at least 2 options
4. **Invalid correct answer**: The correct answer must reference an existing option
5. **Inconsistent formatting**: Mixing different formats within the same file

### Validation Tools

Use the interactive mode for format validation:

```bash
txttoqti-edu --interactive
```

Or programmatic validation:

```python
from txttoqti import QuestionValidator
from txttoqti.parser import QuestionParser

parser = QuestionParser()
questions = parser.parse("questions.txt")

validator = QuestionValidator()
for question in questions:
    is_valid, errors = validator.validate(question)
    if not is_valid:
        print(f"Question {question.number}: {errors}")
```

## Best Practices

1. **Consistency**: Use the same format throughout a question bank
2. **Clarity**: Write clear, unambiguous questions and options
3. **Testing**: Validate your format before conversion
4. **Encoding**: Always save files in UTF-8 encoding
5. **Backup**: Keep original text files as backup before conversion

## Troubleshooting

### Format Detection Issues
- Ensure consistent question numbering
- Check that all required elements are present
- Verify correct answer format matches option format

### Character Encoding Problems
- Save files as UTF-8
- Avoid copying from word processors that add hidden characters
- Use plain text editors

### Conversion Errors
- Run format validation first
- Check for trailing spaces or empty lines
- Ensure proper line endings (Unix/Linux: LF, Windows: CRLF)

For additional help with question formatting, use the interactive troubleshooting mode:

```bash
txttoqti-edu --interactive
```