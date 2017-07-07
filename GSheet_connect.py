import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pygsheets
# need to save the service key file as client_secret.json in same directory as project
class GSheet_connector():
    def __init__(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('Job-Board-Scraper-Config.json', scope)
        self.client = gspread.authorize(creds)

    def processor(self,inputRows):
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        spreadsheet = self.client.open("career_board")

        #clear all worksheets, except the first one
        while True:
            try:
                spreadsheet.del_worksheet(spreadsheet.sheet1)
            except :
                remove_sheet = spreadsheet.sheet1
                remove_sheet.update_title("going_to_remove")
                break

        spreadsheet.add_worksheet("sheet1",800,5)
        spreadsheet.del_worksheet(spreadsheet.sheet1)

        #start inserting record (recerse order)
        sheet = spreadsheet.sheet1
        print ("start inserting the job records...")
        for job in inputRows:
            sheet.insert_row([job[0], job[1], job[2], job[4]], 1)

        print ("almost finish, wrapping up...")
        #insert the first row
        sheet.insert_row(['Company', 'JobTitle', 'JobURL', 'Location'], 1)

        return "Successfully import data to Google Sheet: \n https://docs.google.com/a/hof.capital/spreadsheets/d/1iz7q_-OJIrwVsCuuMyrV9tcYiw2Gc1myeub6qXRPiD0/edit?usp=sharing"

