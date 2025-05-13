# import fitz
# import textwrap
# import requests
# import json
# from sklearn.feature_extraction.text import TfidfVectorizer

# API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
# API_TOKEN = "your-api-token-here"
# HEADERS = {'x-api-token': API_TOKEN, 'Content-Type': 'application/json'}

# # Step 1: Extract text from the PDF
# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text

# # Step 2: Chunk the text
# def chunk_text(text, chunk_size=2000):
#     return textwrap.wrap(text, chunk_size)

# # Step 3: Create Embeddings (TF-IDF or use OpenAI embeddings)
# vectorizer = TfidfVectorizer()
# chunks = chunk_text(extract_text_from_pdf("your_pdf_file.pdf"))
# vectors = vectorizer.fit_transform(chunks)

# def get_relevant_chunk(query):
#     query_vector = vectorizer.transform([query])
#     similarity = (vectors * query_vector.T).toarray()
#     return chunks[similarity.argmax()]

# # Step 4: Query OpenAI
# def build_prompt(relevant_chunk, user_question):
#     prompt = f"Context:\n{relevant_chunk}\n\nQuestion: {user_question}\nAnswer:"
#     return prompt

# def query_openai(messages):
#     payload = {
#         "model": "gpt-3.5-turbo",
#         "messages": [{"role": "system", "content": "You are a helpful assistant."},
#                      {"role": "user", "content": messages}],
#         "max_tokens": 500,
#         "temperature": 0.5
#     }
#     response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
#     return response.json()["choices"][0]["message"]["content"]

# # Step 5: Query user
# question = "leave policy for employees"
# relevant_chunk = get_relevant_chunk(question)
# messages = build_prompt(relevant_chunk, question)
# response = query_openai(messages)
# print(response)


import os
import requests
import json
import time
import fitz  # PyMuPDF

API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_TOKEN = "your-api-token-here"  # Replace with actual token
DOC_DOWNLOAD_URL = "https://your-company-domain.com/handbooks"  

HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json'
}

# Extract text from all PDFs in the docs folder
def load_pdf_documents(doc_folder="docs"):
    documents = []
    if not os.path.exists(doc_folder):
        print(f"Folder not found: {doc_folder}")
        return documents

    for filename in os.listdir(doc_folder):
        file_path = os.path.join(doc_folder, filename)
        if filename.endswith(".pdf"):
            try:
                with fitz.open(file_path) as doc:
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    documents.append((filename, text.strip()))
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    return documents

# Build prompt for OpenAI
def build_prompt(docs, user_question):
    context = "\n\n---\n\n".join([f"# {name}\n{content}" for name, content in docs])
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that answers questions only from the provided company documents. "
                "If the answer is not present, say: 'I don't have this information.' "
                f"Also mention: 'User can download the related handbooks and documents from the following URL: {DOC_DOWNLOAD_URL}'"
            )
        },
        {
            "role": "user",
            "content": f"{context}\n\n---\n\nQuestion: {user_question}"
        }
    ]
    return messages

# Query OpenAI Wrapper API
def query_openai(messages, retries=3, backoff=2):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 512,
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

# Main loop
def main():
    print("Loading PDF documents...")
    documents = load_pdf_documents()
    if not documents:
        print("No PDF documents found in 'docs/' folder.")
        return

    print("Documents loaded. Ask your questions!")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ")
        if question.strip().lower() == "exit":
            break

        messages = build_prompt(documents, question)
        response = query_openai(messages)
        print(f"\nHashBot: {response}\n")

if __name__ == "__main__":
    main()
