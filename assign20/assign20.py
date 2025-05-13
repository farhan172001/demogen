import pandas as pd
import os
import requests
import json


INPUT_FILE = "students_marks.xlsx"
API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
API_TOKEN = "your-api-token-here"  
HEADERS = {
    'x-api-token': API_TOKEN,
    'Content-Type': 'application/json'
}

# === Department Criteria ===
DEPARTMENTS = {
    "Mechanical Engineering": lambda row: row['Physics'] > 90 and row['Chemistry'] > 85 and row['Maths'] > 60,
    "Computer Engineering": lambda row: row['Physics'] > 60 and row['Chemistry'] > 60 and row['Maths'] > 90,
    "Electrical Engineering": lambda row: row['Physics'] > 95 and row['Chemistry'] > 60 and row['Maths'] > 90
}

# === Load Excel Data ===
def load_student_data(filepath):
    return pd.read_excel(filepath)

# === Filter and Save ===
def assign_and_save(students_df):
    summary = {}
    for dept, criteria in DEPARTMENTS.items():
        eligible = students_df[students_df.apply(criteria, axis=1)]
        eligible.to_excel(f"{dept.replace(' ', '_')}.xlsx", index=False)
        summary[dept] = eligible.shape[0]
    return summary

# === Generate Report using OpenAI ===
def generate_summary_report(summary_dict):
    content = "\n".join([f"{dept}: {count} students assigned" for dept, count in summary_dict.items()])
    prompt = f"""Generate a brief report based on the following student assignment summary:

{content}

The report should highlight how students were assigned to departments based on eligibility and overall distribution."""

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant and professional report writer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
        "temperature": 0.5
    }

    response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
    return response.json()["choices"][0]["message"]["content"]

# === Save Report ===
def save_report(text, filename="department_assignment_report.txt"):
    with open(filename, "w") as f:
        f.write(text)


if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
    else:
        print("Reading student data...")
        students_df = load_student_data(INPUT_FILE)

        print("Assigning students to departments...")
        summary = assign_and_save(students_df)

        print("Generating report via OpenAI...")
        report = generate_summary_report(summary)

        print("Saving report...")
        save_report(report)

        print("\n✅ Assignment complete. Files generated:")
        for dept in DEPARTMENTS:
            print(f"- {dept.replace(' ', '_')}.xlsx")
        print("- department_assignment_report.txt")
