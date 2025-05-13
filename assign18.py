import os
import requests
import json
import time

API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_TOKEN = "your-api-token-here"  # Replace this with your actual token

HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json'
}

def load_documents(doc_folder="docs"):
    docs = []
    if not os.path.exists(doc_folder):
        print(f"Folder not found: {doc_folder}")
        return docs

    for filename in os.listdir(doc_folder):
        file_path = os.path.join(doc_folder, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                docs.append((filename, content))
    return docs

def build_prompt(docs, user_question):
    context = "\n\n---\n\n".join([f"# {name}\n{content}" for name, content in docs])
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that answers questions only from the provided company documents. If the answer is not present, say: 'I don't have this information.'"
        },
        {
            "role": "user",
            "content": f"{context}\n\n---\n\nQuestion: {user_question}"
        }
    ]
    return messages

def query_openai(messages, retries=3, backoff=2):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0,
        "top_p": 1
    }

    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"[Attempt {attempt+1}] Error {response.status_code}: {response.text}")
                time.sleep(backoff ** attempt)
        except Exception as e:
            print(f"[Attempt {attempt+1}] Exception: {e}")
            time.sleep(backoff ** attempt)
    return "Failed to get a response from the model."

def main():
    print("Loading documents...")
    documents = load_documents()
    if not documents:
        print("No documents found. Please add files in the 'docs/' folder.")
        return

    print("Documents loaded. Ask your questions!")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ")
        if question.strip().lower() == "exit":
            break

        messages = build_prompt(documents, question)
        response = query_openai(messages)
        print(f"HashBot: {response}\n")

if __name__ == "__main__":
    main()
