import json
import requests
import subprocess
import os

# === CONFIGURATION ===
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_KEY = "YOUR_API_KEY"  # 🔑 Replace this with your actual API key
MMDC_PATH = r"C:\Users\fkhan9\AppData\Roaming\npm\mmdc.cmd"  # Update path if needed

# === FUNCTION TO CALL THE MODEL ===
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
        print("❌ Error calling API:", e)
        return ""

# === VALIDATION FUNCTION ===
def validate_mermaid_code(code):
    stripped = code.strip()
    return stripped.startswith("flowchart TD") or stripped.startswith("graph TD")

# === STRIP CODE BLOCK FENCING ===
def clean_mermaid_code(code):
    if "```" in code:
        code = code.strip().replace("```mermaid", "").replace("```", "").strip()
    return code

# === SAVE TO FILE ===
def save_mermaid_file(code, filename="diagram.mmd"):
    with open(filename, "w") as f:
        f.write(code)

# === RENDER USING MMDC ===
def render_mermaid(filename="diagram.mmd", output="diagram.png"):
    try:
        subprocess.run([MMDC_PATH, "-i", filename, "-o", output], check=True)
        print(f"\n✅ Diagram rendered and saved as: {output}")
    except Exception as e:
        print("❌ Rendering failed. Make sure Mermaid CLI is installed.")
        print("Error:", e)

# === MAIN SCRIPT ===
if __name__ == "__main__":
    print("📥 Describe your system or process. Example:")
    print("User enters credentials → Auth service verifies → JWT issued → Token sent → Dashboard accessed")
    user_description = input("\n🧾 Your description:\n")

    # Step 1: Generate MermaidJS Code
    system_prompt = "Convert the following system/process description into a MermaidJS diagram using 'flowchart TD' format only. Do not wrap in code blocks."
    mermaid_code = call_model(system_prompt, user_description)
    mermaid_code = clean_mermaid_code(mermaid_code)

    # Step 2: Validate
    if not validate_mermaid_code(mermaid_code):
        print("\n⚠️ Mermaid code validation failed. Attempting auto-fix...")
        fix_prompt = "Fix the following MermaidJS diagram code. Ensure it's in correct 'flowchart TD' syntax and don't wrap in code block."
        mermaid_code = call_model(fix_prompt, mermaid_code)
        mermaid_code = clean_mermaid_code(mermaid_code)

    # Step 3: Save and Render
    print("\n🧪 Mermaid Code to Render:\n")
    print(mermaid_code)

    save_mermaid_file(mermaid_code)
    render_mermaid()

    print("\n🎉 Done! Check the generated diagram image.")

# === Requirements ===
# pip install requests
# npm install -g @mermaid-js/mermaid-cli
# Make sure 'mmdc' is added to PATH or update MMDC_PATH in script
# User submits login → Auth service verifies → On success JWT is issued → Token goes to frontend → Dashboard is displayed
# User submits login credentials → Authentication service verifies them → If valid, issues a JWT token → Token is stored on the client side → User accesses the dashboard → Dashboard shows personalized data from the database
