import fitz
import textwrap
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer

API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_TOKEN = "your-api-token-here"
HEADERS = {'x-api-token': API_TOKEN, 'Content-Type': 'application/json'}

# Step 1: Extract text from the PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Step 2: Chunk the text
def chunk_text(text, chunk_size=2000):
    return textwrap.wrap(text, chunk_size)

# Step 3: Create Embeddings (TF-IDF or use OpenAI embeddings)
vectorizer = TfidfVectorizer()
chunks = chunk_text(extract_text_from_pdf("your_pdf_file.pdf"))
vectors = vectorizer.fit_transform(chunks)

def get_relevant_chunk(query):
    query_vector = vectorizer.transform([query])
    similarity = (vectors * query_vector.T).toarray()
    return chunks[similarity.argmax()]

# Step 4: Query OpenAI
def build_prompt(relevant_chunk, user_question):
    prompt = f"Context:\n{relevant_chunk}\n\nQuestion: {user_question}\nAnswer:"
    return prompt

def query_openai(messages):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "system", "content": "You are a helpful assistant."},
                     {"role": "user", "content": messages}],
        "max_tokens": 500,
        "temperature": 0.5
    }
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    return response.json()["choices"][0]["message"]["content"]

# Step 5: Query user
question = "leave policy for employees"
relevant_chunk = get_relevant_chunk(question)
messages = build_prompt(relevant_chunk, question)
response = query_openai(messages)
print(response)
