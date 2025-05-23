import fitz  # PyMuPDF
import textwrap
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# === CONFIG ===
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_TOKEN = "your-api-token-here"  # Replace with your actual token
HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json'
}

# === STEP 1: Extract text from PDF ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# === STEP 2: Chunk the text ===
def chunk_text(text, chunk_size=2000):
    return textwrap.wrap(text, chunk_size)

# === STEP 3: Find most relevant chunk using TF-IDF ===
def get_relevant_chunk(query, vectorizer, vectors, chunks, threshold=0.1):
    query_vector = vectorizer.transform([query])
    similarity_scores = (vectors * query_vector.T).toarray().flatten()
    best_score = np.max(similarity_scores)
    
    if best_score < threshold:
        return None  # Return None if no relevant chunk is found
    
    best_index = np.argmax(similarity_scores)
    return chunks[best_index]

# === STEP 4: Build the prompt for OpenAI ===
def build_prompt(relevant_chunk1, relevant_chunk2, question):
    return f"""You are a helpful assistant.

Context from Document 1 (Adult General Checkup):
{relevant_chunk1}

Context from Document 2 (Child General Checkup):
{relevant_chunk2}

Question: {question}

Answer:"""

# === STEP 5: Query OpenAI ===
def query_openai(prompt):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.5
    }
    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    return response.json()["choices"][0]["message"]["content"]

# === MAIN FLOW ===
if __name__ == "__main__":
    # Load and chunk Document 1 (Adult General Checkup)
    text1 = extract_text_from_pdf("Document1.pdf")
    chunks1 = chunk_text(text1)
    
    # Vectorize Document 1
    vectorizer1 = TfidfVectorizer()
    vectors1 = vectorizer1.fit_transform(chunks1)

    # Load and chunk Document 2 (Child General Checkup)
    text2 = extract_text_from_pdf("Document2.pdf")
    chunks2 = chunk_text(text2)
    
    # Vectorize Document 2
    vectorizer2 = TfidfVectorizer()
    vectors2 = vectorizer2.fit_transform(chunks2)

    # # Combine all chunks for vectorization
    # all_chunks = chunks1 + chunks2
    # vectorizer = TfidfVectorizer()
    # vectors = vectorizer.fit_transform(all_chunks)

    # Ask the user for questions dynamically
    print("Please enter your questions below. Type 'exit' to stop.")
    while True:
        question = input("Enter your question: ")
        
        if question.lower() == "exit":
            print("Exiting program...")
            break
        
        # Find relevant chunks for the question in both documents
        relevant_chunk1 = get_relevant_chunk(question, vectorizer1, vectors1, chunks1)
        relevant_chunk2 = get_relevant_chunk(question, vectorizer2, vectors2, chunks2)

        # If no relevant chunk is found for a document, handle gracefully
        if not relevant_chunk1:
            relevant_chunk1 = "No relevant information found in Document 1."
        if not relevant_chunk2:
            relevant_chunk2 = "No relevant information found in Document 2."

        # Build the prompt and get the answer
        prompt = build_prompt(relevant_chunk1, relevant_chunk2, question)
        answer = query_openai(prompt)

        # Output the answer
        print(f"\nQuestion: {question}")
        print(f"Answer: {answer}\n" + "-" * 80)


# What are the differences between the Pediatric Concerns section in Document 1 and Document 2?

# "What are the differences in the 'Vital Signs' section between Document 1 (Adult Report) and Document 2 (Children Report)?"

# "How does the 'Immunization Record' section in Document 1 compare to the one in Document 2?"

# "Are there any notable differences in the 'Doctor’s Recommendations' section for adults and children?"

# "What is the distinction between the 'Developmental Milestones' section in Document 2 and 'Medical History' in Document 1?"


# "How does the 'Height' data in Document 1 (Adult Report) differ from the 'Height' data in Document 2 (Children Report)?"

# "What variations can be found between the 'Weight' section for adults in Document 1 and children in Document 2?"

# "How does the immunization record differ for children and adults in terms of recommended vaccinations in both reports?"

# "What are the differences in 'Pediatric Concerns' in Document 2 compared to the medical concerns mentioned in Document 1?"

# "What are the key differences between the 'Growth Advice' section for children in Document 2 and for adults in Document 1?"