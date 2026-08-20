from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
import json
import re
import logging

#configure Logging

logging.basicConfig(level = logging.INFO , format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_llm():
    try:
        return ChatGoogleGenerativeAI(
            model = "gemini-3.6-flash",
            google_api_key = os.getenv("GEMINI_API_KEY")
        )
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        raise Exception(f"Failed to retreive the AI Model: {str(e)}")

def create_quiz_prompt(pdf_content, num_questions, difficulty, question_type):

    selected_types = ", ".join(question_type)

    prompt = f"""
You are an AI quiz generator.

Your task is to create a quiz using ONLY the information contained in the document below.

DOCUMENT:
---------------------
{pdf_content}
---------------------

QUIZ REQUIREMENTS:

Number of questions: {num_questions}
Difficulty: {difficulty}
Allowed question types: {selected_types}


DIFFICULTY RULES:

Easy:
- Test basic facts, definitions, names, terms, and simple understanding.

Medium:
- Test understanding of concepts and simple application.

Hard:
- Test analysis, comparison, reasoning, and deeper understanding.

IMPORTANT:
Every question and answer MUST be based only on the document.
Do not use outside knowledge.


QUESTION TYPE RULES:

1. MCQ

If the question type is "MCQ":

- "type" MUST be exactly "MCQ".
- Provide exactly 4 options.
- Only ONE option can be correct.
- "correct_answer" MUST exactly match one of the four options.
- The options must be relevant to the question.


2. True / False

If the question type is "True / False":

- "type" MUST be exactly "True / False".
- The question must be a statement that can clearly be classified as True or False.
- Do NOT provide multiple-choice options.
- "options" MUST be an empty array [].
- "correct_answer" MUST be exactly "True" or "False".
- The statement must be based only on the document.


3. Fill in the blanks

If the question type is "Fill in the blanks":

- "type" MUST be exactly "Fill in the blanks".
- The question must contain a blank represented by "_____".
- Do NOT provide multiple-choice options.
- "options" MUST be an empty array [].
- "correct_answer" must contain the missing word or phrase.
- The answer must be directly supported by the document.


4. Mixed

If the question type is "Mixed":

- Create a combination of:
  - MCQ
  - True / False
  - Fill in the blanks

- Follow all rules for each respective question type.


QUESTION DISTRIBUTION:

If the user selects more than one question type, distribute the questions reasonably among the selected types.

For example:

If the selected types are:
["MCQ", "True / False"]

and the user requests 10 questions:

- Generate approximately 5 MCQs.
- Generate approximately 5 True / False questions.

If only one type is selected, ALL questions must use that type.


OUTPUT FORMAT:

Return ONLY valid JSON.

Do NOT include:
- Markdown
- ```json
- Explanations outside the JSON
- Extra text
- Comments


Each question MUST follow this structure:

For MCQ:

{{
    "question_number": 1,
    "question": "Question text",
    "type": "MCQ",
    "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
    ],
    "correct_answer": "Option A",
    "explanation": "Brief explanation based on the document"
}}


For True / False:

{{
    "question_number": 2,
    "question": "A statement based on the document.",
    "type": "True / False",
    "options": [],
    "correct_answer": "True",
    "explanation": "Brief explanation based on the document"
}}


For Fill in the blanks:

{{
    "question_number": 3,
    "question": "The process of _____ converts light energy into chemical energy.",
    "type": "Fill in the blanks",
    "options": [],
    "correct_answer": "photosynthesis",
    "explanation": "Brief explanation based on the document"
}}


FINAL RULES:

- Generate exactly {num_questions} questions.
- Use ONLY the selected question types.
- Every question must have a correct answer.
- Every question must have an explanation.
- Every question must have a "question_number".
- MCQ must have exactly 4 options.
- True / False must have options: [].
- Fill in the blanks must have options: [].
- Do not mix question formats.
- Return valid JSON only.
"""

    return prompt

def create_fallback_quiz(num_questions):
    fallback_questions = []

    for i in range(num_questions):
        fallback_questions.append(
            {
                "question": "Unable to generate this question at the moment.",
                "type": "MCQ",
                "options": [
                    "Option A",
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "correct_answer": "Not available",
                "explanation": "Please try again later."
            }
        )

    return fallback_questions

def validate_quiz_data(quiz_data, num_questions: int) -> bool:
    """Validate the structure of parsed quiz data."""
    try:
        # Check if quiz is a list
        if not isinstance(quiz_data, list):
            return False
 
        # Check number of questions
        if len(quiz_data) != num_questions:
            return False
 
        required_fields = [
            "question",
            "options",
            "correct_answer",
            "explanation"
        ]
 
        for question in quiz_data:
            # Check required keys exist
            for field in required_fields:
                if field not in question:
                    return False
 
            # Check options are available
            if not isinstance(question["options"], list):
                return False
 
            # Check correct answer exists
            if not question["correct_answer"]:
                return False
 
        return True
 
    except Exception as e:
        logger.error(f"Quiz validation error: {str(e)}")
        return False
 
 
def parse_quiz_response(response: str, num_questions: int):
    """Parse the raw LLM response text into a Python list of question dicts, and validate it."""
    try:
        if isinstance(response, list):
            response = "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in response
            )
            
        response = response.strip()
 
        # Remove markdown code fences if Gemini adds them, anywhere in the string
        response = re.sub(r"^```json\s*|^```\s*|```$", "", response, flags=re.MULTILINE).strip()
 
        # Extract the JSON array even if the model added stray text around it
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if not match:
            raise Exception("No JSON array found in response")
 
        quiz_data = json.loads(match.group())
 
        # Validate structure before handing it back to the caller
        if not validate_quiz_data(quiz_data, num_questions):
            logger.error("Parsed quiz data failed validation")
            raise Exception("Quiz data failed validation")
 
        return quiz_data
 
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise Exception("Failed to parse quiz response")
 
    except Exception as e:
        logger.error(f"Error parsing quiz response: {str(e)}")
        raise Exception(f"Quiz parsing failed: {str(e)}")
def format_quiz_with_answers(quiz_data):
    """Format quiz questions for display, separating the question/options
    from the answer-reveal info (correct answer + explanation) so the UI
    can show questions first and reveal answers afterward."""
    formatted_quiz = []
 
    for idx, question in enumerate(quiz_data, start=1):
        formatted_question = {
            "question_number": idx,
            "question": question.get("question"),
            "type": question.get("type", "MCQ"),
            "options": question.get("options", []),
            "answer_reveal": {
                "correct_answer": question.get("correct_answer"),
                "explanation": question.get("explanation", "")
            }
        }
        formatted_quiz.append(formatted_question)
 
    return formatted_quiz
 
 
def generate_quiz(pdf_content: str, num_questions: int, difficulty: str, question_type: list):
    """Generate a quiz from document content using the LLM, with a fallback quiz on failure."""

    try:

        llm = get_llm()

        prompt = create_quiz_prompt(
            pdf_content,
            num_questions,
            difficulty,
            question_type
        )

        logger.info(
            f"Generating quiz: {num_questions} questions, "
            f"{difficulty} difficulty, {question_type} type"
        )

        response = llm.invoke(
            [HumanMessage(content=prompt)]
        )

        quiz_data = parse_quiz_response(
            response.content,
            num_questions
        )

        logger.info("Quiz generated successfully")

        return format_quiz_with_answers(quiz_data)

    except Exception as e:

        logger.error(
            f"Quiz generation failed, using fallback quiz: {str(e)}"
        )

        return format_quiz_with_answers(
            create_fallback_quiz(num_questions)
        )
 