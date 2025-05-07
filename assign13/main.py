import os
import json
import requests
import time
import glob
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# === CONFIG ===
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
HEADERS = {
    'x-api-token': '',  # Keep blank as per instructions
    'Content-Type': 'application/json'
}

SNIPPET_DIR = "snippets"
MODEL_NAME = "all-MiniLM-L6-v2"

# === INITIAL SETUP ===
embedder = SentenceTransformer(MODEL_NAME)
snippet_texts = []
snippet_files = []

# Load snippets and embed them
for path in glob.glob(f"{SNIPPET_DIR}/*.txt"):
    with open(path, 'r', encoding='utf-8') as file:
        code = file.read()
        snippet_texts.append(code)
        snippet_files.append(path)

snippet_embeddings = embedder.encode(snippet_texts)
index = faiss.IndexFlatL2(snippet_embeddings[0].shape[0])
index.add(np.array(snippet_embeddings))

# === UTILS ===
def post_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Retry {attempt+1}] Error: {e}")
            time.sleep(1)
    raise Exception("Max retries exceeded.")

def chat_with_model(system_prompt, user_prompt, model="gpt-3.5-turbo"):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "max_tokens": 500
    }
    response = post_with_retry(payload)
    return response['choices'][0]['message']['content'].strip()

# === CORE ===
def retrieve_snippets(requirement, top_k=3):
    query_embed = embedder.encode([requirement])
    scores, indices = index.search(query_embed, top_k)
    return [snippet_texts[i] for i in indices[0]]

def generate_code(requirement, retrieved_snippets):
    prompt = f"""You are a Python coding assistant.
User wants: {requirement}

Use the following code references (if helpful):
{retrieved_snippets}

Now generate a clean initial implementation in Python."""
    return chat_with_model("You are an expert Python developer.", prompt)

def refactor_code(initial_code):
    prompt = f"""Refactor the following Python code for clarity, efficiency, and style:
```python
{initial_code}
```"""
    return chat_with_model("You are a senior Python code reviewer.", prompt)

# === MAIN ===
def main():
    requirement = input("Describe your coding requirement: ")

    print("\n🔍 Retrieving relevant code snippets...")
    retrieved = retrieve_snippets(requirement)
    retrieved_str = "\n---\n".join(retrieved)

    print("\n🛠️ Generating initial code...")
    initial_code = generate_code(requirement, retrieved_str)
    print("\nInitial Code:\n", initial_code)

    print("\n🧹 Refactoring code...")
    final_code = refactor_code(initial_code)
    print("\n✅ Final Refactored Code:\n", final_code)

    # Optional: save to file
    with open("generated_code.py", "w", encoding="utf-8") as f:
        f.write(final_code)
        print("\n💾 Code saved to generated_code.py")

if __name__ == "__main__":
    main()
