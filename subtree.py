import sqlite3
import requests
import json

# SQLite database file
DB_FILE = "lifelist.db"

# Open Tree of Life API URL for induced subtree
API_URL = "https://api.opentreeoflife.org/v3/tree_of_life/induced_subtree"

# Function to call the Open Tree of Life API for induced subtree
def call_induced_subtree(ott_ids):
    headers = {"content-type": "application/json"}
    payload = {"ott_ids": ott_ids, "format": "arguson"}
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        return {"error": f"API call failed with status code {response.status_code}"}

# Function to fetch OTT IDs from the database
def fetch_ott_ids(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Query to fetch OTT IDs where OTT ID is not null
    cursor.execute("""
        SELECT ott_id
        FROM api_results
        WHERE ott_id IS NOT NULL
    """)
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]  # Extract only the OTT IDs into a list

# Main script logic
def main():
    # Fetch OTT IDs from the database
    ott_ids = fetch_ott_ids(DB_FILE)

    if not ott_ids:
        print("No OTT IDs found in the database.")
        return

    # Call the API with the OTT IDs
    api_result = call_induced_subtree(ott_ids)

    # Output the response to a file
    with open("induced_subtree_result.json", "w") as outfile:
        json.dump(api_result, outfile, indent=4)

    print(f"Induced subtree response saved to 'induced_subtree_result.json'.")

# Run the script
if __name__ == "__main__":
    main()
