import os
import pandas as pd
import requests
import base64
import azure.functions as func
from datetime import datetime

app = func.FunctionApp()

@app.schedule(schedule="0 */2 * * * *", arg_name="timer", run_on_startup=False, use_monitor=True)
def check_exceptions(timer: func.TimerRequest):

    print(f"[{datetime.utcnow()}] Checking Application Insights for exceptions...")

    # ===========================
    # CONFIG FROM ENVIRONMENT
    # ===========================
    APP_ID = os.getenv("APP_ID")
    AI_API_KEY = os.getenv("AI_API_KEY")
    PAT = os.getenv("AZURE_DEVOPS_PAT")
    ORG = "pavani5696"
    PROJECT = "Practice"
    WORK_ITEM_TYPE = "Issue"

    if not APP_ID or not AI_API_KEY or not PAT:
        print("❌ Missing environment variables. Ensure APP_ID, AI_API_KEY, and AZURE_DEVOPS_PAT are set.")
        return

    # Encode PAT for Basic Auth
    token = base64.b64encode(f":{PAT}".encode()).decode()
    devops_url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/workitems/{WORK_ITEM_TYPE}?api-version=7.0"

    devops_headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Basic {token}"
    }

    # ===========================
    # APPLICATION INSIGHTS QUERY
    # ===========================
    query = """
    exceptions
    | where timestamp > ago(5m)
    | project timestamp, message, type
    | order by timestamp desc
    """
    ai_url = f"https://api.applicationinsights.io/v1/apps/{APP_ID}/query"
    ai_headers = {"x-api-key": AI_API_KEY}

    try:
        response = requests.get(ai_url, params={"query": query}, headers=ai_headers)

        if response.status_code != 200:
            print("❌ Failed to fetch data from Application Insights:", response.text)
            return

        data = response.json()
        if "tables" not in data or not data["tables"]:
            print("No exceptions returned from Application Insights.")
            return

        rows = data["tables"][0]["rows"]
        columns = [c["name"] for c in data["tables"][0]["columns"]]
        df = pd.DataFrame(rows, columns=columns)

        if df.empty:
            print("No new exceptions found.")
            return

        processed = set()  # track duplicates within this run

        for i, row in df.iterrows():
            timestamp = str(row["timestamp"])
            message = row.get("message", "No message")
            ex_type = row.get("type", "Unknown")

            # Unique key to avoid duplicates
            unique_key = timestamp + message
            if unique_key in processed:
                continue

            title = f"Exception Detected: {ex_type}"
            desc = f"Time: {timestamp}\nType: {ex_type}\nError: {message}"

            body = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/System.Description", "value": desc}
            ]

            r = requests.post(devops_url, headers=devops_headers, json=body)
            print(f"ADO POST response: {r.status_code} - {r.text}")

            if r.status_code in [200, 201]:
                print(f"✅ Work item created for exception at {timestamp}")
                processed.add(unique_key)
            else:
                print(f"❌ Failed to create work item at {timestamp}")

    except Exception as e:
        print("❌ Error during processing:", str(e))

    print("Sleeping until next schedule...\n")
