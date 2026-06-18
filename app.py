from flask import Flask, render_template, request, session
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
import os
from dotenv import load_dotenv
 
app = Flask(__name__)
app.secret_key = "secret123"

load_dotenv("api.env")

api_key = os.getenv("API_KEY")

print("API_KEY= ",api_key)

genai.configure(api_key=api_key)

model = genai.GenerativeModel("models/gemini-flash-lite-latest")
# 🏠 Home
@app.route("/")
def home():
    session.clear()
    return render_template("index.html")


# 🎤 Start Interview
@app.route("/start", methods=["POST"])
def start():

    session["role"] = request.form["role"]
    session["q_no"] = 0
    session["answers"] = []

    prompt = f"""
    Generate exactly 5 technical interview questions for a {session['role']}.

    Return only questions separated by ||.
    """

    response = model.generate_content(prompt)

    questions = response.text.split("||")

    session["questions"] = questions

    return render_template(
        "interview.html",
        question=questions[0],
        qno=1,
        total=5
    )


# 🔁 Next Question + Evaluation
@app.route("/answer", methods=["POST"])
def answer():

    user_answer = request.form["answer"]

    answers = session.get("answers", [])
    answers.append(user_answer)

    session["answers"] = answers
    session["q_no"] += 1

    q_no = session["q_no"]
    questions = session["questions"]

    if q_no < len(questions):

        return render_template(
            "interview.html",
            question=questions[q_no],
            qno=q_no + 1,
            total=len(questions)
        )

    interview_text = ""

    for q, a in zip(questions, answers):
        interview_text += f"""
Question: {q}

Answer: {a}

"""

    prompt = f"""
You are an interview evaluator.

Evaluate the candidate answers below.

{interview_text}

Rules:
- Keep the response under 80 words.
- Return only the format below.
- Do not add explanations, introductions, conclusions, markdown, or extra text.

Format:

Score: <number>/100

Weaknesses:
- point 1
- point 2
- point 3
"""

    result = model.generate_content(prompt).text

    return render_template(
        "result.html",
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

