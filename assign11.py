import requests
import json
import time

# Constants
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
HEADERS = {
    'x-api-token': '',  # <-- Leave blank, you fill it later
    'Content-Type': 'application/json',
    'Cookie': 'csrftoken=Ia7mAreRCxbvmPwNUbiRdOqdf74jrT2X'
}

# Parameters
MODEL_NAME = "gpt-3.5-turbo"
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds
MAX_TOKENS = 150
TEMPERATURE = 0.7
TOP_P = 1


def call_openai_api(messages, max_tokens=MAX_TOKENS):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": TEMPERATURE,
        "top_p": TOP_P
    }
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(RETRY_BACKOFF * (attempt + 1))
    raise Exception("API call failed after multiple retries.")


def summarize_text(user_input_text):
    system_prompt = {
        "role": "system",
        "content": "You are an expert summarizer. Summarize the text in around 100 words."
    }
    user_prompt = {
        "role": "user",
        "content": f"Summarize the following text in 100 words:\n\n{user_input_text}"
    }
    return call_openai_api([system_prompt, user_prompt])


def paraphrase_summary(summary_text):
    system_prompt = {
        "role": "system",
        "content": "You simplify text for younger audiences while keeping meaning intact."
    }
    user_prompt = {
        "role": "user",
        "content": f"Paraphrase the following summary for a younger audience:\n\n{summary_text}"
    }
    return call_openai_api([system_prompt, user_prompt])


def main():
    # Sample input text (replace with actual user input)
    user_input_text = (
        "In recent years, the rapid development of technology has drastically transformed the way we live and work. "
        "From the rise of artificial intelligence to the proliferation of smart devices, technology continues to shape "
        "industries around the world. These innovations have led to increased efficiency and the creation of new jobs, "
        "although concerns about data privacy and job displacement persist."
    )

    print("📌 Summarizing...")
    summary = summarize_text(user_input_text)
    print("\nOriginal Summary:\n", summary)

    print("\n🔁 Paraphrasing...")
    paraphrased = paraphrase_summary(summary)
    print("\nParaphrased Summary:\n", paraphrased)


if __name__ == "__main__":
    main()
