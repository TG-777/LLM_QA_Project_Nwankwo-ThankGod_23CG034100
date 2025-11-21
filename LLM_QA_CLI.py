import requests
import re

# Replace with your chosen LLM API endpoint and key
LLM_API_URL = "https://api.openai.com/v1/completions"  
API_KEY = ""

def preprocess_question(question):
    # Lowercase, remove punctuation, simple tokenization
    question = question.lower()
    question = re.sub(r'[^\w\s]', '', question)
    tokens = question.split()
    return " ".join(tokens)

def ask_llm_api(question):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": question,
        "max_tokens": 200
    }
    response = requests.post(LLM_API_URL, headers=headers, json=data)
    response.raise_for_status()
    answer = response.json()['choices'][0]['text'].strip()
    return answer

def main():
    print("=== NLP Question-Answering CLI ===")
    question = input("Enter your question: ")
    processed_question = preprocess_question(question)
    print(f"Processed Question: {processed_question}")
    answer = ask_llm_api(processed_question)
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()
