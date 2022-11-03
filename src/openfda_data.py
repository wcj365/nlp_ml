#!/usr/local/env python3

import json
import requests
import pandas as pd

BATCH_SIZE = 1000    # Maximum allowed by OpenFDA is 1000
FETCH_SIZE = 100000  # Enforcement report has around 29k records
DATE_RANGE = "[20200101+TO+20221231]"   # This is the accepted format to specify report date range
API_URL = f"https://api.fda.gov/device/enforcement.json?search=report_date:{DATE_RANGE}&limit={BATCH_SIZE}&skip="

def get_enforcement_data():

    i = 0
    contents = []
    while True:
        print(f"Retriving batch #{i + 1}.", end=" ")
        skip = i * BATCH_SIZE
        resp = requests.get(API_URL + str(skip))
        json_resp = json.loads(resp.text) 

        # OpenFDA imposes a limit on skip at 25000 meaning the maximum # of records retrived is 26000
        if "error" in json_resp:      
            print(f'Encountered an error: {json_resp["error"]["code"]}:{json_resp["error"]["message"]}.')
            print(f"DATA Request APT: {API_URL + str(skip)}")
            print("The remaining records are not retrived.")
            break

        contents += json_resp["results"]
        total = int(json_resp["meta"]["results"]["total"])

        i += 1
        print(f"Retrived {BATCH_SIZE * i}. Remaining {total - BATCH_SIZE * i}.")

        if i == 1:
            print(f"Total number of enforcement records: {total}.")

        if BATCH_SIZE * i >= FETCH_SIZE:
            break

        if BATCH_SIZE * i > total:
            break

    return pd.DataFrame(contents)  


if __name__ == "__main__":

    df = get_enforcement_data()

    df.to_csv("./data/enforcement_reports.csv", index=False)

    print(df.shape)  
    print(df.info()) 
    print(df.head())