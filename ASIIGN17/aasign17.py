import ast
import json
import time
import requests
import os

# ✅ CONFIGURATION
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_TOKEN = "your-api-token-here"  # Replace this with your actual token

HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json'
}

# ✅ Extracts function names and docstrings from Python file
def extract_docstrings(file_path):
    print(f"🔍 Attempting to open file: {file_path}")
    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} does not exist!")
        return []

    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
            print(f"📝 File content length: {len(file_content)} characters")
            print(f"📝 First 100 characters: {file_content[:100]}")
            print(f"📂 Verifying actual file content:\n{file_content}")

        tree = ast.parse(file_content)
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node)
                if doc:
                    print(f"✅ Found function with docstring: {node.name}")
                    results.append((node.name, doc))
                else:
                    print(f"⚠️ Function without docstring: {node.name}")
        print(f"📊 Total functions with docstrings found: {len(results)}")
        return results
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        return []

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

# ✅ API wrapper with retries and backoff
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
                print(f"[Attempt {attempt+1}] Error {response.status_code}: {response.text}")
                time.sleep(backoff ** attempt)
        except Exception as e:
            print(f"[Attempt {attempt+1}] Exception: {e}")
            time.sleep(backoff ** attempt)
    return "❌ Error: Failed to get model response"

# ✅ Save results to Markdown
def save_to_markdown(doc_entries, output_file="api_docs.md"):
    if not doc_entries:
        print("❌ Warning: No documentation entries to save.")
    with open(output_file, 'w') as f:
        for entry in doc_entries:
            f.write(entry.strip() + "\n\n---\n\n")
    print(f"✅ Documentation saved to {output_file}.")

# ✅ Main function
def generate_api_docs(input_file):
    input_file = os.path.abspath(input_file)
    print(f"📂 Processing file: {input_file}")

    functions = extract_docstrings(input_file)
    if not functions:
        print("❌ No functions with docstrings found in the file.")
        save_to_markdown(["No API documentation generated."])
        return

    print(f"🔍 Found {len(functions)} functions with docstrings.")
    all_docs = []

    for func_name, docstring in functions:
        print(f"🚧 Processing function: {func_name}")
        prompt1 = create_transformation_prompt(func_name, docstring)
        transformed_doc = call_openai_with_retries(prompt1)

        prompt2 = create_best_practices_prompt(docstring)
        review = call_openai_with_retries(prompt2)

        full_doc = f"""### `{func_name}`

{transformed_doc}

**📝 Style Review:**  
{review}"""
        all_docs.append(full_doc)

    save_to_markdown(all_docs)

# ✅ Entry point
if __name__ == "__main__":
    print("\n==== Python Docstring API Documentation Generator ====\n")

    # ✅ Use absolute path to avoid file-not-found errors
    sample_code_path = os.path.abspath("assignment17/sample_code.py")
    if not os.path.exists(sample_code_path):
        print(f"❌ sample_code.py not found at {sample_code_path}")
    else:
        print(f"✅ Using sample_code.py at: {sample_code_path}")
        generate_api_docs(sample_code_path)
