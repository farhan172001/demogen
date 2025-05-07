import requests
import json
import time
import numpy as np
from typing import List, Tuple
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION ---
API_URL_CHAT = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_URL_EMBED = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/embeddings/"
API_TOKEN = ""  # Leave blank for evaluation, insert in production
HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json'
}

# --- FAQ Data Store ---
FAQS = [
    {
        "question": "How do I recover my password?",
        "answer": "To reset your password, go to the account settings page, click on 'Forgot Password,' and follow the instructions sent to your registered email."
    },
    {
        "question": "How can I change my email address?",
        "answer": "Navigate to your profile settings, select 'Change Email,' and confirm the new email through a verification link."
    },
    {
        "question": "How do I delete my account?",
        "answer": "To delete your account, go to Settings > Privacy > Delete Account. This process is irreversible."
    }
]

# --- Retry Wrapper ---
def post_with_retry(url, payload, headers, max_retries=3, wait=2):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[Retry {attempt+1}] Error: {e}")
            time.sleep(wait)
    raise Exception("Max retries exceeded.")

# --- Step 1: Expand User Query ---
def expand_query(user_query: str) -> str:
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Expand the user's query using synonyms and related terms."},
            {"role": "user", "content": f"Original query: {user_query}"}
        ],
        "temperature": 0.7,
        "max_tokens": 64
    }
    data = post_with_retry(API_URL_CHAT, payload, HEADERS)
    return data['choices'][0]['message']['content'].strip()

# --- Step 2: Embed Text ---
def get_embedding(text: str) -> List[float]:
    payload = {
        "model": "text-embedding-ada-002",
        "input": text
    }
    data = post_with_retry(API_URL_EMBED, payload, HEADERS)
    return data['data'][0]['embedding']

# --- Step 3: Retrieve Most Relevant FAQ ---
def retrieve_faq(expanded_query: str) -> Tuple[str, str]:
    query_emb = np.array(get_embedding(expanded_query)).reshape(1, -1)

    best_score = -1
    best_faq = None

    for faq in FAQS:
        faq_emb = np.array(get_embedding(faq["question"])).reshape(1, -1)
        score = cosine_similarity(query_emb, faq_emb)[0][0]
        if score > best_score:
            best_score = score
            best_faq = faq

    return best_faq["question"], best_faq["answer"]

# --- Step 4: Generate Tailored Final Answer ---
def generate_final_answer(user_query: str, faq_answer: str) -> str:
    prompt = f"""
Use the following FAQ answer to respond more personally to the user query.

User Query: {user_query}
FAQ Answer: {faq_answer}

Tailored Answer:
    """
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Tailor the following FAQ answer to the user query."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 128
    }
    data = post_with_retry(API_URL_CHAT, payload, HEADERS)
    return data['choices'][0]['message']['content'].strip()

# --- Main Workflow ---
def main():
    user_query = input("Enter your question: ").strip()
    expanded = expand_query(user_query)
    faq_q, faq_a = retrieve_faq(expanded)
    final_answer = generate_final_answer(user_query, faq_a)

    print("\n--- Result ---")
    print(f"Expanded Query:\n{expanded}\n")
    print(f"Retrieved FAQ:\nQ: {faq_q}\nA: {faq_a}\n")
    print(f"Final Answer:\n{final_answer}")

if __name__ == "__main__":
    main()
