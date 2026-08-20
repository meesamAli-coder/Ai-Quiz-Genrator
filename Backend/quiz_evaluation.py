def calculate_score(quiz, user_answers):
    score = 0

    for question in quiz:

        question_number = question["question_number"]

        correct_answer = question["answer_reveal"]["correct_answer"]

        user_answer = user_answers.get(question_number)

        if user_answer == correct_answer:
            score += 1

    total_questions = len(quiz)

    percentage = (score / total_questions) * 100

    return score, total_questions, percentage

def evaluate_answers(quiz, user_answers):
    results = []

    for question in quiz:

        question_number = question["question_number"]

        correct_answer = question["answer_reveal"]["correct_answer"]

        explanation = question["answer_reveal"]["explanation"]

        user_answer = user_answers.get(question_number)

        is_correct = user_answer == correct_answer

        results.append({
            "question_number": question_number,
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": explanation
        })

    return results