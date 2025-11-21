from flask import Flask, render_template, request, jsonify
import requests
import re
import os

app = Flask(__name__)


LLM_API_URL = "gemini.google.com"
API_KEY = os.environ.get("GOOGLE_KEY")  

def preprocess_question(question):
    """Lowercase, remove punctuation"""
    question = question.lower()
    question = re.sub(r'[^\w\s]', '', question)
    return question

def ask_llm_api(question):
    """Send the processed question to the LLM API"""
    """Send the processed question to the LLM API.

    If `LLM_API_URL` is the default placeholder ('/'), return a mock/fallback
    response so local frontend testing works without an external LLM configured.
    """
    # Local fallback to avoid recursive calls or failing requests during local testing
    if not LLM_API_URL or LLM_API_URL == "/":
        return f"(mock) Processed question: {question}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": question,
        "max_tokens": 200
    }
    try:
        response = requests.post(LLM_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['text'].strip()
    except requests.RequestException as e:
        raise RuntimeError(f"LLM request failed: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    processed_question = ""
    if request.method == "POST":
        # Accept either form-encoded (traditional submit) or JSON (AJAX/fetch)
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            question = (payload.get("question") if isinstance(payload, dict) else "") or ""
            question = question.strip()
        else:
            # use get to avoid KeyError if the form field is missing
            question = request.form.get("question", "").strip()

        if question:
            processed_question = preprocess_question(question)
            try:
                answer = ask_llm_api(processed_question)
            except Exception as e:
                # surface a friendly error message instead of crashing
                answer = f"Error contacting LLM API: {e}"
        else:
            answer = "Please enter a question."

        # If the request came from fetch() sending JSON, return JSON instead of HTML
        if request.is_json:
            return jsonify({"answer": answer})
    return render_template("index.html", answer=answer, processed_question=processed_question)

if __name__ == "__main__":
    # Render and other PaaS typically provide PORT in the environment.
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug_env = os.environ.get("DEBUG", "false").lower()
    debug = debug_env in ("1", "true", "yes")
    app.run(host=host, port=port, debug=debug)

