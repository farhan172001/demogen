import ast
import json
import time
import requests

# ✅ CONFIGURATION
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_TOKEN = "your-api-token-here"  # Replace with your actual token

HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json'
}

# ✅ Extracts function names and docstrings from Python file
def extract_docstrings(file_path):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            if doc:
                results.append((node.name, doc))
    return results

# ✅ Prompt 1: Transform docstring into user-facing documentation
def create_transformation_prompt(func_name, docstring):
    return [
        {
            "role": "system",
            "content": "You are an expert technical writer. Convert raw Python docstrings into clean, user-facing API documentation in Markdown format."
        },
        {
            "role": "user",
            "content": f"Function: {func_name}\n\n'''{docstring}'''"
        }
    ]

# ✅ Prompt 2: Check against best practices
def create_best_practices_prompt(docstring):
    return [
        {
            "role": "system",
            "content": "You are a Python documentation reviewer. Given the following docstring, check if it follows Google Style and PEP-257 standards. Suggest improvements briefly if needed."
        },
        {
            "role": "user",
            "content": docstring
        }
    ]

# ✅ Wrapper API call with retries
def call_openai_with_retries(messages, retries=3, backoff=2):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.5,
        "top_p": 1
    }
    for attempt in range(retries):
        try:
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"[Attempt {attempt+1}] Error {response.status_code}, retrying...")
                time.sleep(backoff ** attempt)
        except Exception as e:
            print(f"[Attempt {attempt+1}] Exception: {e}")
            time.sleep(backoff ** attempt)
    return "❌ Error: Failed to get model response"

# ✅ Save final documentation to Markdown
def save_to_markdown(doc_entries, output_file="api_docs.md"):
    with open(output_file, 'w') as f:
        for entry in doc_entries:
            f.write(entry.strip() + "\n\n---\n\n")

# ✅ Main function
def generate_api_docs(input_file):
    functions = extract_docstrings(input_file)
    all_docs = []

    for func_name, docstring in functions:
        print(f"🚧 Processing function: {func_name}")
        
        # Step 1: Transform docstring
        prompt1 = create_transformation_prompt(func_name, docstring)
        transformed_doc = call_openai_with_retries(prompt1)

        # Step 2: Check best practices
        prompt2 = create_best_practices_prompt(docstring)
        review = call_openai_with_retries(prompt2)

        # Combine results
        full_doc = f"""### `{func_name}`

{transformed_doc}

**📝 Style Review:**  
{review}
"""
        all_docs.append(full_doc)

    save_to_markdown(all_docs)
    print("✅ Documentation saved to `api_docs.md`.")

# ✅ Entry point
if __name__ == "__main__":
    generate_api_docs("sample_code.py")
