import json
import requests
import subprocess
import os

API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_KEY = "YOUR_API_KEY"  # Replace with your key

def call_model(system_prompt, user_prompt):
    headers = {
        'x-api-token': API_KEY,
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "gpt-4",
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    })
    try:
        response = requests.post(API_URL, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error calling API:", e)
        return ""

def validate_mermaid_code(code):
    required_keywords = ["graph", "flowchart", "-->"]
    return any(kw in code for kw in required_keywords)

def save_mermaid_file(code, filename="diagram.mmd"):
    with open(filename, "w") as f:
        f.write(code)

def render_mermaid(filename="diagram.mmd", output="diagram.png"):
    try:
        subprocess.run(["mmdc", "-i", filename, "-o", output], check=True)
        print(f"Diagram saved as {output}")
    except Exception as e:
        print("Rendering failed. Make sure mermaid-cli is installed and working.")
        print("Error:", e)

# === MAIN FLOW ===
if __name__ == "__main__":
    user_description = input("Describe your system or process:\n")

    # Step 1: Generate MermaidJS Code
    system_prompt = "Convert the following system/process description into a MermaidJS flowchart. Use 'flowchart TD' syntax."
    mermaid_code = call_model(system_prompt, user_description)

    # Step 2: Validate the Code
    if not validate_mermaid_code(mermaid_code):
        print("\n⚠️ Mermaid code validation failed. Attempting to fix it...")
        fix_prompt = "Fix this MermaidJS diagram code. Correct syntax and structure."
        mermaid_code = call_model(fix_prompt, mermaid_code)

    # Step 3: Save and Render the Diagram
    save_mermaid_file(mermaid_code)
    render_mermaid()

    print("\n✅ Final Mermaid Code:\n")
    print(mermaid_code)
    
# npm install -g @mermaid-js/mermaid-cli
# mmdc -h

# User enters credentials → Auth service verifies credentials → On success, a JWT token is issued → Token sent to frontend → User accesses dashboard
