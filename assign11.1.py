import json
import requests
import time

# ✅ API Setup
API_URL_CHAT = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
HEADERS = {
    'x-api-token': '',  # Leave blank as instructed
    'Content-Type': 'application/json'
}

# ✅ Sample FAQs
FAQS = [
    {
        "question": "How do I recover my password?",
        "answer": "To reset your password, go to the account settings page, click on 'Forgot Password,' and follow the instructions sent to your registered email."
    },
    {
        "question": "How can I change my email address?",
        "answer": "Go to your profile settings and click on 'Edit Email.' Enter your new email address and confirm it via the link sent."
    },
    {
        "question": "How to delete my account?",
        "answer": "To delete your account, contact support or use the 'Delete Account' option under account settings. This action is permanent."
    }
]

# ✅ Retry logic
def post_with_retry(url, payload, headers, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Retry {attempt+1}] Error: {e}")
            time.sleep(delay)
    raise Exception("Max retries exceeded.")

# ✅ Step 1: Expand Query
def expand_query(user_query):
    system_prompt = "You are a helpful assistant that rewrites user questions using synonyms and related terms to improve search results."
    user_prompt = f"Rewrite the user's query to include synonyms and related terms: {user_query}"
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 64,
        "top_p": 1
    }
    data = post_with_retry(API_URL_CHAT, payload, HEADERS)
    return data['choices'][0]['message']['content'].strip()

# ✅ Step 2: Retrieve most relevant FAQ using GPT
def retrieve_faq(expanded_query):
    prompt = f"User query: {expanded_query}\n\nChoose the most relevant FAQ from the list:\n"
    for idx, faq in enumerate(FAQS):
        prompt += f"\nFAQ {idx+1}:\nQ: {faq['question']}\nA: {faq['answer']}\n"
    prompt += "\nRespond with the FAQ number (e.g., 1, 2, or 3) that best answers the user's query."

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a smart FAQ retrieval engine."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 10
    }

    data = post_with_retry(API_URL_CHAT, payload, HEADERS)
    choice = data['choices'][0]['message']['content'].strip()

    try:
        index = int(choice) - 1
        return FAQS[index]['question'], FAQS[index]['answer']
    except:
        raise ValueError(f"Invalid response from model: {choice}")

# ✅ Step 3: Tailor the Final Answer
def generate_final_answer(user_query, faq_answer):
    prompt = f"User asked: {user_query}\nFAQ answer: {faq_answer}\n\nWrite a final tailored answer that addresses the user query based on the FAQ."
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150,
        "top_p": 1
    }

    data = post_with_retry(API_URL_CHAT, payload, HEADERS)
    return data['choices'][0]['message']['content'].strip()

# ✅ Main Execution
def main():
    user_query = input("Enter your question: ")
    expanded = expand_query(user_query)
    faq_q, faq_a = retrieve_faq(expanded)
    final_answer = generate_final_answer(user_query, faq_a)

    print("\n--- OUTPUT ---")
    print(f"\nExpanded Query: {expanded}")
    print(f"\nRetrieved FAQ:\nQ: {faq_q}\nA: {faq_a}")
    print(f"\nFinal Answer:\n{final_answer}")

if __name__ == "__main__":
    main()
