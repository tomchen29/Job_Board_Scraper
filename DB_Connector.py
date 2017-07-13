import gspread   #does not work with GAE
import MySQLdb
from oauth2client.service_account import ServiceAccountCredentials
import airtable

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

class mysqlObj():
    def __init__(self):
        self.db = MySQLdb.connect(host="35.190.157.173", user="root", passwd="", db="hof")
        # localhost
        # db = MySQLdb.connect(host="localhost", user="root", passwd="292929", db="hof")
        self.cur = self.db.cursor()

    def truncate_mysql_by_companies(self, companyNameList):
        # clear the company record
        for companyName in companyNameList:
            self.cur.execute("DELETE FROM job_board WHERE Company ='" + companyName + "'")
            self.db.commit()

    def mysql_insert(self, output):
        for job in output:
            try:
                command = "INSERT INTO job_board (Company, JobTitle, JobURL, Location) VALUES ('{}','{}','{}','{}')".format(
                    job[0], job[1], job[2], job[4])
                self.cur.execute(command)
                self.db.commit()
            except UnicodeEncodeError:
                print ""

    def mysql_close(self):
        self.db.close()

class AirTable_Connector():
    def __init__(self):
        #BASE_ID is determined by template, while API_KEY can be looked up under account
        self.at = airtable.Airtable('appbtafAIFaEzOwJh', 'keyud5Dhufnrqqhp2')
        self.worksheet = (self.at.get('Job_Board'))

    def update_records(self,job_input):
        record_dict = self.worksheet['records']

        delete_id_bucket = []
        for row in record_dict:
            delete_id_bucket.append(row['id'])

        #delete all the previous rows
        for delete_row_id in delete_id_bucket:
            self.at.delete('Job_Board',str(delete_row_id))

        for job in job_input:
            input_dict_string = {
            "CompanyName": job[0],
            "Job Title": job[1],
              "JobURL": job[2],
              "Location": job[4]}

            self.at.create('Job_Board', input_dict_string)
