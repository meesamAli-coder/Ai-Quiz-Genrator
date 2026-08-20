import json
import os
from datetime import datetime


HISTORY_FILE = "quiz_history.json"


def save_quiz_result(
    document_name,
    num_questions,
    difficulty,
    score,
    percentage,
    time_taken
):
    result = {
        "date": datetime.now().strftime("%d-%b-%Y %H:%M"),
        "document": document_name,
        "questions": num_questions,
        "difficulty": difficulty,
        "score": f"{score}/{num_questions}",
        "percentage": percentage,
        "time": time_taken
    }

    history = []

    if os.path.exists(HISTORY_FILE):

        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)

    history.append(result)

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)


def load_quiz_history():

    if not os.path.exists(HISTORY_FILE):
        return []

    with open(HISTORY_FILE, "r") as file:
        history = json.load(file)

    return history