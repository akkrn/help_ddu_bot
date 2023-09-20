import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ["https://googlepis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("sh/gcreds.json", scope)
client = gspread.authorize(creds)
tables = ["users", "penalties", "defects", "questions"]

for table in tables:
    sheet=client.open(table).sheet1
    with open(f"/var/www/help_ddu_bot/{table}.csv", "r") as file:
        csv_contents = file.read()
        sheet.clear()
        sheet.append_rows(csv_contents)

