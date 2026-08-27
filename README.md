# AI Quiz Generator

An AI-powered web app that turns a text-based PDF document into an interactive quiz. Upload your study material, choose your settings, and get instant, AI-generated questions — graded automatically with a full answer review and a history dashboard.

Built with **Python**, **Streamlit**, and **Google Gemini** (via **LangChain**).

---

##  Features

- **PDF Upload** — extracts text directly from an uploaded, text-based PDF
- **AI-Generated Quizzes** — questions are generated strictly from the document content using Google Gemini, with no outside knowledge
- **Customizable Settings** — choose number of questions, difficulty (Easy / Medium / Hard), and question type (MCQ, True/False, Fill in the Blanks, or a mix)
- **Optional Timer** — set a time limit and the quiz auto-submits when it runs out
- **Instant Scoring** — automatic grading with percentage score
- **Answer Review** — see every question with your answer, the correct answer, and an explanation
- **Dashboard** — tracks total quizzes taken, average score, and best score over time
- **Quiz History** — every attempt is saved and viewable in a history table

---

##  Screenshots

### Quiz Generation
<img width="1000" height="500" alt="Screenshot 2026-08-27 010620" src="https://github.com/user-attachments/assets/a7d26652-3a7f-4878-b99a-f747d60570fa" />



### Quiz Results
<img width="1000" height="500" alt="Screenshot 2026-08-27 010749" src="https://github.com/user-attachments/assets/f0750904-96f9-4ea2-adf0-bd65a39473b0" />


### Dashboard
<img width="100" height="500" alt="Screenshot 2026-08-27 010844" src="https://github.com/user-attachments/assets/e0f3e78b-e3f7-45da-a85f-120b5404604c" />




---

##  Architecture

```text
PDF Upload
    ↓
Document Extractor
    ↓
Cleaned Text
    ↓
AI Engine (prompt construction)
    ↓
Google Gemini (via LangChain)
    ↓
JSON Quiz Response
    ↓
Validation & Formatting
    ↓
Streamlit Quiz UI
    ↓
Quiz Evaluation
    ↓
Score + Answer Review
    ↓
Quiz History / Dashboard
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | [Streamlit](https://streamlit.io/) |
| AI Model | [Google Gemini](https://ai.google.dev/) via [LangChain](https://www.langchain.com/) |
| PDF Parsing | [pypdf](https://pypi.org/project/pypdf/) |
| Data Handling | [pandas](https://pandas.pydata.org/) |
| Config / Secrets | [python-dotenv](https://pypi.org/project/python-dotenv/) |
| Live Timer | [streamlit-autorefresh](https://pypi.org/project/streamlit-autorefresh/) |

---

## Project Structure

```
Project/
│
├── frontend/
│   └── app.py                  # Streamlit UI — the entire user-facing app
│
└── backend/
    ├── ai_engine.py            # Builds the AI prompt, calls Gemini, parses/validates the quiz JSON
    ├── document_extractor.py   # Extracts raw text from an uploaded PDF
    ├── quiz_evaluation.py      # Scores answers and builds the detailed answer review
    └── quiz_history.py         # Saves and loads past quiz attempts (JSON file)
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- A [Google Gemini API key](https://ai.google.dev/)

### Installation

```bash
# Clone the repository
git clone https://github.com/<meesamAli-coder>/ai-quiz-generator.git
cd ai-quiz-generator

```

### Configuration

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_api_key_here
```

### Run the app

```bash
streamlit run frontend/app.py
```

The app will open automatically in your browser (usually at `http://localhost:8501`).

---

## 📖 How It Works

1. Upload a PDF document.
2. Choose the number of questions, difficulty, question type(s), and an optional time limit.
3. Click **Generate Quiz** — the text is extracted and sent to Gemini with a structured prompt that keeps every question grounded in the document.
4. Answer the quiz in the app, with a live countdown if a time limit was set.
5. Submit (or let the timer run out) to get an instant score and a full answer review with explanations.
6. Check the dashboard at the bottom to see your quiz history and overall stats.

---

##  Roadmap

- [ ] Support additional document formats (DOCX, TXT)
- [ ] OCR support for scanned/image-based PDFs
- [ ] Add support for additional LLM providers
- [ ] Replace local JSON storage with a database
- [ ] Deploy the application

---

##  Known Limitations

- Currently supports **text-based PDFs only** — scanned/image-only PDFs won't extract text yet (OCR is on the roadmap)
- DOCX and TXT are not yet supported
- Quiz history is stored in a local JSON file — fine for personal/local use, not built for concurrent multi-user access

---

##  Author

**Meesam**
Data Science Student, COMSATS University Islamabad

---


