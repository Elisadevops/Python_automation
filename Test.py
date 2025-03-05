
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python

python3 --version

pip3 install pandas gspread oauth2client


Go to Google Cloud Console: https://console.cloud.google.com/

Steps:
pip3 install pandas gspread oauth2client




import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

print("🔄 Starting script...")

# Step 1: Authenticate with Google Sheets API
SERVICE_ACCOUNT_FILE = "acquired-voice-452303-c3-72708a278c1e.json"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
print("✅ Google Sheets authentication successful!")

# Step 2: Open Google Spreadsheet
SPREADSHEET_NAME = "RawData"  # Spreadsheet name
RAW_WORKSHEET = "RawData"  # Existing sheet with raw data
PROCESSED_WORKSHEET = "ProcessedData"  # New sheet for processed data

try:
    sheet = client.open(SPREADSHEET_NAME).worksheet(RAW_WORKSHEET)
    print(f"✅ Opened Spreadsheet: {SPREADSHEET_NAME} | Worksheet: {RAW_WORKSHEET}")
except Exception as e:
    print(f"❌ Error opening spreadsheet: {e}")
    exit()

# Step 3: Read data from "Sheet1"
data = sheet.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    print("⚠️ No data found in Sheet1!")
    exit()

print("✅ Data loaded from Sheet1!")

# Step 4: Ensure column names match
df.columns = df.columns.str.strip()  # Remove accidental spaces in column names

# Step 5: Group by Practitioner & Income Category, summing up commissions
try:
    grouped_df = df.groupby(["Practitioner", "Income Category"], as_index=False).agg({
        "Commission Subtotal": "sum",
        "Commission Total": "sum"
    })
    print("✅ Data grouped successfully!")
except Exception as e:
    print(f"❌ Error during data grouping: {e}")
    exit()

# Step 6: Convert DataFrame to list format for writing to Google Sheets
data_to_write = [grouped_df.columns.tolist()] + grouped_df.values.tolist()  # Add header row

# Step 7: Check if "ProcessedData" sheet exists, if not create it
try:
    processed_sheet = client.open(SPREADSHEET_NAME).worksheet(PROCESSED_WORKSHEET)
    print(f"✅ Found existing worksheet: {PROCESSED_WORKSHEET}")
except gspread.exceptions.WorksheetNotFound:
    print(f"🔄 Worksheet '{PROCESSED_WORKSHEET}' not found. Creating new sheet...")
    processed_sheet = client.open(SPREADSHEET_NAME).add_worksheet(title=PROCESSED_WORKSHEET, rows="1000", cols="10")
    print(f"✅ New worksheet '{PROCESSED_WORKSHEET}' created!")

# Step 8: Append new data without clearing old data
try:
    processed_sheet.append_rows(data_to_write, value_input_option="RAW")
    print("✅ Processed data appended to 'ProcessedData' worksheet successfully!")
except Exception as e:
    print(f"❌ Error writing to 'ProcessedData': {e}")

print("🎉 Script execution completed!")
