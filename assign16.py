import json
import requests

API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"

def call_model(system_prompt, user_prompt):
    headers = {
        'x-api-token': 'Your_API_KEY',  # Replace with your actual API key
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "gpt-4",
        "max_tokens": 4096
    })
    response = requests.post(API_URL, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def summarize_document(document):
    system_prompt = "Summarize the following document into bullet points."
    user_prompt = document
    return call_model(system_prompt, user_prompt)

def classify_content(summary):
    system_prompt = "Classify the following summary into one of these categories: 'Entertainment', 'Technology', 'Finance'."
    user_prompt = summary
    return call_model(system_prompt, user_prompt)

def restyle_summary(summary, audience_type="formal"):
    if audience_type == "formal":
        system_prompt = "Restyle the following summary to make it sound formal and professional."
    else:
        system_prompt = "Restyle the following summary to make it sound casual and conversational."
    
    user_prompt = summary
    return call_model(system_prompt, user_prompt)

# Main script
document = """Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems.
These processes include learning, reasoning, and self-correction. AI has applications in various fields, including robotics, healthcare, finance, and entertainment."""

summary = summarize_document(document)
classification = classify_content(summary)
formal_summary = restyle_summary(summary, audience_type="formal")
casual_summary = restyle_summary(summary, audience_type="casual")

# Final output
print("\nOriginal Document:", document)
print("\nSummary:", summary)
print("\nClassification:", classification)
print("\nFormal Restyled Summary:", formal_summary)
print("\nCasual Restyled Summary:", casual_summary)
