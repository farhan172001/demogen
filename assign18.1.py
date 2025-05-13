import os
import fitz  # PyMuPDF
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
        if os.path.isfile(file_path) and filename.endswith(".pdf"):
            try:
                doc = fitz.open(file_path)
                content = ""
                for page in doc:
                    content += page.get_text()
                docs.append((filename, content))
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
    return docs

def split_into_chunks(text, max_chars=2000):
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

def build_prompt(chunk, user_question):
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that answers questions only from the provided company documents. If the answer is not present, say: 'I don't have this information.'"
        },
        {
            "role": "user",
            "content": f"{chunk}\n\n---\n\nQuestion: {user_question}"
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
                json_response = response.json()
                return json_response["choices"][0]["message"]["content"]
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
        print("No documents found. Please add PDF files in the 'docs/' folder.")
        return

    print("Documents loaded. Ask your questions!")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ")
        if question.strip().lower() == "exit":
            break

        all_chunks = []
        for name, content in documents:
            chunks = split_into_chunks(f"# {name}\n{content}")
            all_chunks.extend(chunks)

        final_answers = []

        for chunk in all_chunks:
            messages = build_prompt(chunk, question)
            answer = query_openai(messages)
            if answer and "I don't have this information" not in answer:
                final_answers.append(answer)

        if final_answers:
            print("HashBot:\n" + "\n---\n".join(final_answers[:3]))  # Show top 3 chunks’ answers
        else:
            print("HashBot: I don't have this information.\n")

if __name__ == "__main__":
    main()
