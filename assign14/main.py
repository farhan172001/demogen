import os
import json
import requests
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# === CONFIGURATION ===
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_KEY = "YOUR_API_KEY"  # Replace with your key
SNIPPET_DIR = "snippets"
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# === STEP 1: LOAD & EMBED CODE SNIPPETS ===
def load_snippets():
    snippets = []
    filenames = []
    for fname in os.listdir(SNIPPET_DIR):
        with open(os.path.join(SNIPPET_DIR, fname), "r") as f:
            snippets.append(f.read())
            filenames.append(fname)
    return snippets, filenames

def embed_snippets(snippets):
    embeddings = EMBEDDING_MODEL.encode(snippets)
    return np.array(embeddings)

# === STEP 2: RAG: RETRIEVE SNIPPETS RELEVANT TO USER PROMPT ===
def retrieve_relevant_snippets(user_prompt, snippets, snippet_embeddings, top_k=2):
    query_embedding = EMBEDDING_MODEL.encode([user_prompt])[0]
    index = faiss.IndexFlatL2(snippet_embeddings.shape[1])
    index.add(snippet_embeddings)
    distances, indices = index.search(np.array([query_embedding]), top_k)
    return [snippets[i] for i in indices[0]]

# === STEP 3: CALL OPENAI WRAPPER ===
def call_model(system_prompt, user_prompt):
    headers = {
        'x-api-token': API_KEY,
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "gpt-4",
        "max_tokens": 1024
    })
    try:
        response = requests.post(API_URL, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error calling API:", e)
        return ""

# === MAIN FLOW ===
if __name__ == "__main__":
    user_input = input("Describe your coding requirement:\n")

    # Step 1: Load and embed code snippets
    snippets, filenames = load_snippets()
    snippet_embeddings = embed_snippets(snippets)

    # Step 2: Retrieve top matching snippets
    retrieved_snippets = retrieve_relevant_snippets(user_input, snippets, snippet_embeddings)

    # Step 3: Generate initial boilerplate
    system_prompt_1 = "You're a code generator. Use best practices and the following code references to build a solution."
    combined_context = "\n\n".join(retrieved_snippets)
    user_prompt_1 = f"User requirement: {user_input}\n\nCode references:\n{combined_context}"
    initial_code = call_model(system_prompt_1, user_prompt_1)

    # Step 4: Refactor the code
    system_prompt_2 = "You're a senior software engineer. Refactor the following code for clarity, efficiency, and style."
    final_code = call_model(system_prompt_2, initial_code)

    # Step 5: Save output
    with open("final_code.py", "w") as f:
        f.write(final_code)
    print("\n✅ Final Refactored Code:\n")
    print(final_code)
