import sqlite3
import requests
import json

# SQLite database file
DB_FILE = "lifelist.db"

# Open Tree of Life API URL
API_URL = "https://api.opentreeoflife.org/v3/tnrs/match_names"

# Function to call the Open Tree of Life API
def call_api(scientific_name):
    headers = {"content-type": "application/json"}
    payload = {"names": [scientific_name]}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API call failed with status code {response.status_code}"}

# Function to extract OTT ID from API response
def extract_ott_id(api_result):
    try:
        matches = api_result.get("results", [])[0].get("matches", [])
        if matches:
            return matches[0]["taxon"]["ott_id"]
    except (KeyError, IndexError, TypeError):
        pass
    return None

# Function to process the database
def process_database(db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the output table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_results (
            scientific_name TEXT,
            ott_id INTEGER,
            result_doc TEXT
        )
    """)

    # Fetch scientific names where Category is "species"
    cursor.execute("""
        SELECT distinct `Scientific Name`
        FROM lifelist
        WHERE `Category` = "species" AND `Scientific Name` IS NOT NULL
    """)
    rows = cursor.fetchall()

    # Call the API for each row and insert results into the database
    for (scientific_name,) in rows:
        api_result = call_api(scientific_name)
        print(f"Looking up {scientific_name}")
        if "results" in api_result:
            ott_id = extract_ott_id(api_result)
            result_doc = json.dumps(api_result)  # Serialize the API result to JSON
            cursor.execute("""
                INSERT INTO api_results (scientific_name, ott_id, result_doc)
                VALUES (?, ?, ?)
            """, (scientific_name, ott_id, result_doc))
            conn.commit()
            print("Written.")
        else:
            print(f"Error for {scientific_name}: {api_result.get('error', 'Unknown error')}")

    conn.commit()
    conn.close()

# Run the script
process_database(DB_FILE)
