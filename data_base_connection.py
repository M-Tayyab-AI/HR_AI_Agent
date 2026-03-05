import os
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
load_dotenv()

google_service_account=os.getenv("GOOGLE_SERVICE_ACCOUNT")
google_sheet_id=os.getenv("SPREAD_SHEET_KEY")
service_account_info = json.loads(google_service_account)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

client = gspread.authorize(creds)

# Column headers
# headers = ["Name", "Position", "Role", "Current_Salary", "Joining_Date"]
# sheet.update([headers],"A1:E1", )
def get_organization_hierarchy_date():
    # open by name
    # sheet = client.open("Employess_Data").sheet1

    # OR open by ID
    sheet = client.open_by_key(google_sheet_id).sheet1
    data = sheet.get_all_values()
    hierarchy=[]
    for row in data:
        # print(row)
        hierarchy.append(row)
    return hierarchy
# print(get_organization_hierarchy_date())

def update_sheet_by_cell(cell_data:dict):
    # Dictionary par loop chalayein aur har cell ko update karein
    sheet = client.open_by_key(google_sheet_id).sheet1
    for cell, value in cell_data.items():
        sheet.update_acell(cell, value)

def get_all_names():
    sheet = client.open_by_key(google_sheet_id).worksheet("Sheet2")
    data = sheet.get_all_records()
    # Extract only the 'Name' values using a list comprehension
    names = [row['Name'] for row in data]

    return names
