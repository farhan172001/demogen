import json
import requests
import time

API_URL = "https://openai-api-wrapper-urtjok3rza-wl.a.run.app/api/chat/completions/"
HEADERS = {
    'x-api-token': '',  # Leave blank as instructed
    'Content-Type': 'application/json'
}

MOCK_SCHEMA = {
    "Rentals": ["rental_id", "customer_id", "movie_id", "rental_date"],
    "Customers": ["customer_id", "first_name", "last_name", "first_time"],
    "Movies": ["movie_id", "title", "genre"]
}

MAX_RETRIES = 3


def post_with_retry(payload):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[Retry {attempt}] Error: {e}")
            time.sleep(1)
    raise Exception("Max retries exceeded.")


def chat_with_model(system_prompt, user_prompt):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "max_tokens": 256
    }
    response = post_with_retry(payload)
    return response["choices"][0]["message"]["content"].strip()

import sqlite3

def simulate_query(refined_sql):
    # Step 1: Create an in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Step 2: Create tables
    cursor.execute('''CREATE TABLE Customers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        first_time BOOLEAN
    )''')

    cursor.execute('''CREATE TABLE Movies (
        movie_id INTEGER PRIMARY KEY,
        title TEXT,
        genre TEXT
    )''')

    cursor.execute('''CREATE TABLE Rentals (
        rental_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        movie_id INTEGER,
        rental_date TEXT,
        FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
        FOREIGN KEY(movie_id) REFERENCES Movies(movie_id)
    )''')

    # Step 3: Insert mock data
    cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?)", [
        (1, 'Alice', 'Smith', True),
        (2, 'Bob', 'Jones', False),
        (3, 'Charlie', 'Lee', True),
    ])

    cursor.executemany("INSERT INTO Movies VALUES (?, ?, ?)", [
        (1, 'Inception', 'Sci-Fi'),
        (2, 'Titanic', 'Romance'),
        (3, 'The Matrix', 'Sci-Fi'),
    ])

    cursor.executemany("INSERT INTO Rentals VALUES (?, ?, ?, ?)", [
        (1, 1, 1, '2024-12-01'),
        (2, 2, 2, '2024-11-01'),
        (3, 3, 3, '2025-04-10'),
    ])

    try:
        # Step 4: Run the refined SQL
        print("\nRunning SQL Query on mock DB...")
        cursor.execute(refined_sql)
        rows = cursor.fetchall()

        print("\nQuery Result:")
        if not rows:
            print("No results found.")
        else:
            for row in rows:
                print(row)

    except sqlite3.Error as e:
        print("\nSQLite Error:", e)

    finally:
        conn.close()

def main():
    # Step 1: Accept user question
    question = input("Enter your natural language question: ")

    # Step 2: Prepare mock schema
    schema_str = "\n".join([f"Table: {table}\nColumns: {', '.join(cols)}" for table, cols in MOCK_SCHEMA.items()])

    # Step 3: Generate SQL
    system_prompt_gen = "You are an expert database assistant. You will generate SQL queries based on user questions and provided schema."
    user_prompt_gen = f"Schema:\n{schema_str}\n\nUser Question:\n{question}\n\nGenerate a valid SQL query for the above."

    initial_sql = chat_with_model(system_prompt_gen, user_prompt_gen)
    print("\nInitial SQL Generated:\n", initial_sql)

    # Step 4: Refine SQL
    system_prompt_refine = "You are a senior database engineer. Refine or correct any issues in the SQL query based on the schema."
    user_prompt_refine = f"Schema:\n{schema_str}\n\nInitial SQL:\n{initial_sql}\n\nRefine this SQL query."

    refined_sql = chat_with_model(system_prompt_refine, user_prompt_refine)
    # refined_sql = refined_sql.strip()
    
    if refined_sql.startswith("```sql"):
        refined_sql = refined_sql.replace("```sql", "").replace("```", "").strip()
    refined_sql = refined_sql.replace("DATE_SUB(CURDATE(), INTERVAL 30 DAY)", "DATE('now', '-30 day')")
    refined_sql = refined_sql.replace("CURDATE()", "DATE('now')")
    print("\nRefined SQL:\n", refined_sql)
    simulate_query(refined_sql)

    
if __name__ == "__main__":
    main()
