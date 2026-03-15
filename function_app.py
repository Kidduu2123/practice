import os
import pandas as pd
import requests
import base64
import azure.functions as func
from datetime import datetime

app = func.FunctionApp()

@app.schedule(schedule="0 */2 * * * *", arg_name="timer", run_on_startup=False, use_monitor=True)
def check_exceptions(timer: func.TimerRequest):

    print("Checking Application Insights for exceptions...")

    # ===========================
    # CONFIG
    # ===========================
    APP_ID = os.getenv("APP_ID")
    AI_API_KEY = os.getenv("AI_API_KEY")
    PAT = os.getenv("AZURE_DEVOPS_PAT")

    ORG = "pavani5696"
    PROJECT = "Practice"
    WORK_ITEM_TYPE = "Issue"

    token = base64.b64encode(f":{PAT}".encode()).decode()

    devops_url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wit/workitems/${WORK_ITEM_TYPE}?api-version=7.0"

    devops_headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Basic {token}"
    }

    query = """
    exceptions
    | where timestamp > ago(5m)
    | project timestamp, message, type
    | order by timestamp desc
    """

    ai_url = f"https://api.applicationinsights.io/v1/apps/{APP_ID}/query"

    ai_headers = {
        "x-api-key": AI_API_KEY
    }

    try:

        response = requests.get(ai_url, params={"query": query}, headers=ai_headers)

        if response.status_code != 200:
            print("Failed to fetch data:", response.text)
            return

        data = response.json()

        if "tables" not in data or not data["tables"]:
            print("No exceptions returned.")
            return

        rows = data["tables"][0]["rows"]
        columns = [c["name"] for c in data["tables"][0]["columns"]]

        df = pd.DataFrame(rows, columns=columns)

        if df.empty:
            print("No new exceptions found.")
            return

        for i, row in df.iterrows():

            timestamp = str(row["timestamp"])
            message = row.get("message", "No message")
            ex_type = row.get("type", "Unknown")

            title = f"Exception Detected: {ex_type}"

            desc = f"""
Time: {timestamp}
Type: {ex_type}
Error: {message}
"""

            body = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/System.Description", "value": desc}
            ]

            r = requests.post(devops_url, headers=devops_headers, json=body)

            if r.status_code in [200, 201]:
                print(f"Work item created for exception at {timestamp}")
            else:
                print("Failed to create work item:", r.text)

    except Exception as e:
        print("Error:", str(e))
