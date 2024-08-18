import requests
import json
import pandas as pd

url = "https://clinicaltrials.gov/api/v2/studies"

# Query parameters
params = {
    "format": "json",
    "markupFormat": "markdown",
    "postFilter.overallStatus": "COMPLETED"
}

# Headers
headers = {
    "Accept": "application/json"
}

# GET
response = requests.get(url, headers=headers, params=params)

# Check the response status code
if response.status_code == 200:
 
    data = response.json()
    
    # Flatten the JSON data
    df = pd.json_normalize(data['studies'], sep='_')

    # If there are lists within columns, you may want to expand them
    # For example, expanding a 'locations' list into separate rows:
    if 'contactsLocationsModule_locations' in df.columns:
        df = df.explode('contactsLocationsModule_locations')

    # Display the full DataFrame
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_rows', None)     # Show all rows
    print(df)

    # Save the DataFrame to a CSV file if needed
    df.to_csv('clinical_trials_data.csv', index=False)
    
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
