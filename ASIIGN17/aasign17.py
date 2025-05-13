import ast 
import json 
import time 
import requests
import os
import sys

# ✅ CONFIGURATION
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/" 
API_TOKEN = "your-api-token-here"  # Replace with your actual token  

HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json' 
}

# ✅ Extracts function names and docstrings from Python file
def extract_docstrings(file_path):
    print(f"🔍 Attempting to open file: {file_path}")
    if not os.path.exists(file_path):
        print(f"❌ Error: File {file_path} does not exist!")
        # List files in directory to help with debugging
        parent_dir = os.path.dirname(file_path) or "."
        print(f"📁 Files in directory {parent_dir}:")
        for f in os.listdir(parent_dir):
            print(f"   - {f}")
        return []
    
    try:
        print(f"📄 Reading file: {file_path}")
        with open(file_path, 'r') as f:
            file_content = f.read()
            print(f"📝 File content length: {len(file_content)} characters")
            print(f"📝 First 100 characters: {file_content[:100]}")
        
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
    except FileNotFoundError:
        print(f"❌ Error: File {file_path} not found.")
        return []
    except SyntaxError as e:
        print(f"❌ Syntax error in file: {e}")
        return []
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
                print(f"[Attempt {attempt+1}] Error {response.status_code}: {response.text}")
                time.sleep(backoff ** attempt)
        except Exception as e:
            print(f"[Attempt {attempt+1}] Exception: {e}")
            time.sleep(backoff ** attempt)
    return "❌ Error: Failed to get model response"

# ✅ Save final documentation to Markdown
def save_to_markdown(doc_entries, output_file="api_docs.md"):
    if not doc_entries:
        print("❌ Warning: No documentation entries to save.")
    with open(output_file, 'w') as f:
        for entry in doc_entries:
            f.write(entry.strip() + "\n\n---\n\n")
    print(f"✅ Documentation saved to {output_file}.")

# ✅ Main function
def generate_api_docs(input_file):
    # Use proper path handling
    input_file = os.path.normpath(input_file)
    
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
{review}"""
        all_docs.append(full_doc)
     
    save_to_markdown(all_docs)

# ✅ Entry point
if __name__ == "__main__":
    print("\n==== Python Docstring API Documentation Generator ====\n")
    
    # Try different path formats to locate the file
    possible_paths = [
        r"assignment17\sample_code.py",            # Relative with backslash
        "assignment17/sample_code.py",             # Relative with forward slash
        os.path.join("assignment17", "sample_code.py"),  # Using os.path.join
        r"C:\GenAITraning\assignment17\sample_code.py",  # Absolute path 
        os.path.abspath(os.path.join("assignment17", "sample_code.py")) # Absolute using current directory
    ]
    
    # Create a sample file if necessary
    sample_file_content = '''def greet_user(name):
    """Greets a user by name.

    Args:
        name (str): Name of the user.

    Returns:
        str: Greeting message.
    """
    return f"Hello, {name}!"

def add(a, b):
    """Adds two numbers and returns the result.

    Args:
        a (int): First number.
        b (int): Second number.

    Returns:
        int: Sum of a and b.
    """
    return a + b
'''
    
    # Try to find the sample file in possible paths
    found_file = False
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found file at: {path}")
            generate_api_docs(path)
            found_file = True
            break
    
    # If file not found, create it
    if not found_file:
        print("❌ Could not find sample_code.py in any expected location.")
        print("📝 Creating sample_code.py in current directory...")
        
        with open("sample_code.py", "w") as f:
            f.write(sample_file_content)
        
        print(f"✅ Created sample_code.py in: {os.getcwd()}")
        generate_api_docs("sample_code.py")