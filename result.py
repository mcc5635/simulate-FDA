import requests
import json
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# List of publicly traded companies involved in clinical trials
companies = ["MRK","JNJ"]

# Define the window size for the Simple Moving Average (SMA)
window_size = 30

# Calculate startDate and endDate
end_date = datetime.today()
start_date = end_date - timedelta(days=365 * 10)

# Format dates in the format required by yfinance
end_date_str = end_date.strftime('%Y-%m-%d')
start_date_str = start_date.strftime('%Y-%m-%d')

# Initialize an empty DataFrame to store clinical trials data
clinical_trials_df = pd.DataFrame()

# Fetch clinical trials data from ClinicalTrials.gov
url = "https://clinicaltrials.gov/api/v2/studies"
params = {
    "format": "json",
    "markupFormat": "markdown",
    "postFilter.overallStatus": "COMPLETED"
}
headers = {
    "Accept": "application/json"
}

# GET request
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    # Flatten the JSON data into a DataFrame
    clinical_trials_df = pd.json_normalize(data['studies'], sep='_')
    
    # Select and rename relevant columns
    columns_to_keep = {
        'protocolSection_identificationModule_nctId': 'NCT ID',
        'protocolSection_identificationModule_orgStudyIdInfo_id': 'Org Study ID',
        'protocolSection_identificationModule_organization_fullName': 'Organization Name',
        'protocolSection_identificationModule_organization_class': 'Organization Class',
        'protocolSection_statusModule_overallStatus': 'Overall Status',
        'protocolSection_designModule_studyType': 'Study Type',
        'protocolSection_designModule_phases': 'Phases',
        'protocolSection_designModule_designInfo_allocation': 'Allocation',
        'protocolSection_designModule_designInfo_interventionModel': 'Intervention Model',
        'protocolSection_designModule_designInfo_primaryPurpose': 'Primary Purpose',
        'protocolSection_designModule_designInfo_maskingInfo_masking': 'Masking',
        'protocolSection_designModule_enrollmentInfo_count': 'Enrollment Count',
        'protocolSection_designModule_enrollmentInfo_type': 'Enrollment Type',
        'protocolSection_outcomesModule_primaryOutcomes': 'Primary Outcomes',
        'protocolSection_outcomesModule_secondaryOutcomes': 'Secondary Outcomes',
        'protocolSection_eligibilityModule_eligibilityCriteria': 'Eligibility Criteria',
        'protocolSection_eligibilityModule_healthyVolunteers': 'Healthy Volunteers',
        'protocolSection_eligibilityModule_sex': 'Sex',
        'protocolSection_eligibilityModule_minimumAge': 'Minimum Age',
        'protocolSection_eligibilityModule_maximumAge': 'Maximum Age',
        'protocolSection_eligibilityModule_stdAges': 'Standardized Ages',
        'protocolSection_contactsLocationsModule_overallOfficials': 'Overall Officials',
        'protocolSection_contactsLocationsModule_locations': 'Locations',
        'protocolSection_ipdSharingStatementModule_ipdSharing': 'IPD Sharing',
        'protocolSection_ipdSharingStatementModule_description': 'IPD Description',
        'protocolSection_ipdSharingStatementModule_infoTypes': 'IPD Info Types',
        'protocolSection_ipdSharingStatementModule_timeFrame': 'IPD Time Frame',
        'protocolSection_ipdSharingStatementModule_accessCriteria': 'IPD Access Criteria',
        'protocolSection_ipdSharingStatementModule_url': 'IPD URL'
    }
    
    clinical_trials_df = clinical_trials_df[list(columns_to_keep.keys())].rename(columns=columns_to_keep)

    # Initialize a dictionary to store unique entries for each column
    unique_entries = {}

    # Loop through each column and get unique entries
    for column in clinical_trials_df.columns:
        # Convert unhashable types (like lists and dictionaries) to strings
        if clinical_trials_df[column].apply(lambda x: isinstance(x, (list, dict))).any():
            clinical_trials_df[column] = clinical_trials_df[column].apply(lambda x: str(x))
        
        unique_entries[column] = clinical_trials_df[column].unique()

    # Convert the dictionary to a DataFrame for better visualization
    unique_entries_df = pd.DataFrame(dict([(k, pd.Series(v)) for k,v in unique_entries.items()]))

    # Display the DataFrame with unique entries
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', 1000)        # Set the width to avoid line breaks
    pd.set_option('display.max_colwidth', 50)   # Set the maximum column width
    print(unique_entries_df)

else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
