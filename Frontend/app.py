import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import streamlit as st
import Backend.document_extractor as de
import pandas as pd
import time

from Backend.ai_engine import generate_quiz
from Backend.quiz_evaluation import calculate_score, evaluate_answers
from Backend.quiz_history import save_quiz_result, load_quiz_history
from streamlit_autorefresh import st_autorefresh


# ===================================================
# SESSION STATE
# ===================================================

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_start_time" not in st.session_state:
    st.session_state.quiz_start_time = None

if "time_up" not in st.session_state:
    st.session_state.time_up = False

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "results" not in st.session_state:
    st.session_state.results = None

if "score" not in st.session_state:
    st.session_state.score = None


# ===================================================
# PAGE CONFIGURATION
# ===================================================

st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🧠",
    layout="wide"
)


# ===================================================
# SIDEBAR
# ===================================================

st.sidebar.title("⚙️ Quiz Settings")
st.sidebar.markdown("---")

num_questions = st.sidebar.slider(
    "Number of Questions",
    min_value=5,
    max_value=50,
    value=10,
    step=5
)

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

question_type = st.sidebar.multiselect(
    "Question Type",
    [
        "MCQ",
        "True / False",
        "Fill in the Blanks"
    ],
    default=["MCQ"]
)

time_limit = st.sidebar.selectbox(
    "Time Limit",
    [
        "No Limit",
        "5 Minutes",
        "10 Minutes",
        "15 Minutes",
        "20 Minutes",
        "30 seconds"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
    Upload a document and generate an AI-powered quiz.

    Supported Files:
    - PDF
    """
)


# ===================================================
# MAIN PAGE
# ===================================================

st.title("🧠 AI Quiz Generator")

st.write(
    "Generate quizzes instantly from your study material using AI."
)

st.divider()


# ===================================================
# FILE UPLOAD
# ===================================================

uploaded_file = st.file_uploader(
    "📄 Upload your document",
    type=["pdf"]
)


# ===================================================
# GENERATE QUIZ
# ===================================================

generate = st.button(
    "🚀 Generate Quiz",
    use_container_width=True
)


if generate:

    if uploaded_file is None:

        st.warning("Please upload a document first.")

    else:

        extracted_text = de.extract_pdf_text(uploaded_file)

        with st.spinner("Generating your quiz..."):

            quiz = generate_quiz(
                extracted_text,
                num_questions,
                difficulty,
                question_type
            )

            # Reset everything for the new quiz
            st.session_state.quiz = quiz
            st.session_state.quiz_start_time = time.time()
            st.session_state.time_up = False
            st.session_state.user_answers = {}
            st.session_state.submitted = False
            st.session_state.results = None
            st.session_state.score = None


# ===================================================
# DISPLAY QUIZ
# ===================================================

if st.session_state.quiz is not None:

    # ------------------------------------------------
    # SHOW QUIZ ONLY IF NOT SUBMITTED
    # ------------------------------------------------

    if not st.session_state.submitted:

        st.subheader("📝 Quiz")

        # --------------------------------------------
        # TIME LIMITS
        # --------------------------------------------

        time_limits = {
            "No Limit": None,
            "5 Minutes": 5 * 60,
            "10 Minutes": 10 * 60,
            "15 Minutes": 15 * 60,
            "20 Minutes": 20 * 60,
            "30 seconds": 30
        }

        time_limit_seconds = time_limits[time_limit]

        # --------------------------------------------
        # TIMER
        # --------------------------------------------

        if time_limit_seconds is not None:

            st_autorefresh(
                interval=1000,
                key="quiz_timer"
            )

            elapsed_time = (
                time.time()
                - st.session_state.quiz_start_time
            )

            remaining_time = max(
                0,
                time_limit_seconds - int(elapsed_time)
            )

            # Time has finished
            if remaining_time == 0:

                st.session_state.time_up = True

            # Display time-up message
            if st.session_state.time_up:

                st.error(
                    "⏰ Time is up! Your quiz was submitted automatically."
                )

            else:

                minutes = remaining_time // 60
                seconds = remaining_time % 60

                st.warning(
                    f"⏱️ Time Remaining: {minutes:02d}:{seconds:02d}"
                )

        # --------------------------------------------
        # QUESTIONS
        # --------------------------------------------

        user_answers = {}

        for question in st.session_state.quiz:

            question_number = question["question_number"]

            st.markdown(
                f"### Question {question_number}"
            )

            st.write(
                question["question"]
            )

            if question["type"] == "MCQ":

                user_answers[question_number] = st.radio(
                "Select your answer:",
                question["options"],
            key=f"question_{question_number}"
            )


            elif question["type"] == "True / False":

                user_answers[question_number] = st.radio(
                    "Select your answer:",
                    ["True", "False"],
                    key=f"question_{question_number}"
                )


            elif question["type"] == "Fill in the blanks":

                user_answers[question_number] = st.text_input(
                    "Fill in the blank:",
                    key=f"question_{question_number}"
                )

        st.divider()

        # --------------------------------------------
        # SUBMIT BUTTON
        # --------------------------------------------

        submit_quiz = st.button(
            "✅ Submit Quiz",
            use_container_width=True
        )

        # --------------------------------------------
        # MANUAL OR AUTOMATIC SUBMISSION
        # --------------------------------------------

        if (
            submit_quiz
            or st.session_state.time_up
        ):

            # Prevent duplicate submission
            if not st.session_state.submitted:

                # Save current answers
                st.session_state.user_answers = user_answers

                # Mark as submitted
                st.session_state.submitted = True

                # Calculate score
                score, total_questions, percentage = calculate_score(
                    st.session_state.quiz,
                    user_answers
                )

                # Save score
                st.session_state.score = (
                    score,
                    total_questions,
                    percentage
                )

                # Save quiz history
                save_quiz_result(
                    uploaded_file.name,
                    total_questions,
                    difficulty,
                    score,
                    percentage,
                    "Time Up"
                    if st.session_state.time_up
                    else "N/A"
                )

                # Evaluate answers
                results = evaluate_answers(
                    st.session_state.quiz,
                    user_answers
                )

                # Store results in session state
                st.session_state.results = results

                # Force Streamlit to rerun
                st.rerun()


# ===================================================
# DISPLAY RESULTS
# ===================================================

if (
    st.session_state.submitted
    and st.session_state.results is not None
):

    score, total_questions, percentage = (
        st.session_state.score
    )

    # -----------------------------------------------
    # TIME UP MESSAGE
    # -----------------------------------------------

    if st.session_state.time_up:

        st.error(
            "⏰ Time is up! Your quiz was submitted automatically."
        )

    # -----------------------------------------------
    # SCORE
    # -----------------------------------------------

    st.success(
        f"🎉 Your Score: "
        f"{score}/{total_questions} "
        f"({percentage:.0f}%)"
    )

    # -----------------------------------------------
    # ANSWER REVIEW
    # -----------------------------------------------

    st.subheader("📋 Answer Review")

    for result in st.session_state.results:

        if result["is_correct"]:

            st.success(
                f"Question "
                f"{result['question_number']} — Correct"
            )

        else:

            st.error(
                f"Question "
                f"{result['question_number']} — Incorrect"
            )

        st.write(
            f"**Question:** "
            f"{result['question']}"
        )

        st.write(
            f"**Your Answer:** "
            f"{result['user_answer']}"
        )

        if not result["is_correct"]:

            st.write(
                f"**Correct Answer:** "
                f"{result['correct_answer']}"
            )

        st.write(
            f"**Explanation:** "
            f"{result['explanation']}"
        )

        st.divider()


# ===================================================
# DASHBOARD
# ===================================================

st.divider()

st.subheader("Dashboard")

history = load_quiz_history()


if history:

    total_quizzes = len(history)

    average_score = (
        sum(
            item["percentage"]
            for item in history
        )
        / total_quizzes
    )

    best_score = max(
        item["percentage"]
        for item in history
    )

else:

    total_quizzes = 0
    average_score = 0
    best_score = 0


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Quizzes",
        total_quizzes
    )


with col2:

    st.metric(
        "Average Score",
        f"{average_score:.0f}%"
    )


with col3:

    st.metric(
        "Best Score",
        f"{best_score:.0f}%"
    )


# ===================================================
# QUIZ HISTORY
# ===================================================

st.subheader("📜 Quiz History")


if history:

    history_df = pd.DataFrame(history)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No quiz history yet.")