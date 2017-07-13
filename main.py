from job_board_scraper_framework import *
from DB_Connector import *

def scraper_runner(scraper_main,GSheet_connector=None, mysqlObj = None, AirTable_connector = None):
    print "job_board scraping starts ----->"

    #start scrapping
    print "now scraping starship... "
    scraper_main.starship_scraper()

    print "now scraping vida... "
    scraper_main.vida_scraper()

    print "now scraping voiq... "
    scraper_main.voiq_scraper()

    print "now scraping social native... "
    scraper_main.socialnative_scraper()

    print "now scraping regalii... "
    scraper_main.regalii_scraper()

    print "now scraping yup..."
    scraper_main.yup_scraper()

    print "\n all scraping processes completed! Start importing to Google Sheet"

    # store the data to google sheets (Option 1)
    if GSheet_connector != None:
        GSheet_connector.processor(scraper_main.output)

    #store the data to mysql (Option 2)
    if mysqlObj != None:
        mysqlObj.truncate_mysql_by_companies(scraper_main.companyNameList)
        mysqlObj.mysql_insert(scraper_main.output)
        mysqlObj.mysql_close()

    #store the data to airtable (Option 3)
    if AirTable_connector!=None:
        AirTable_connector.update_records(scraper_main.output)

    print "\n import to the appointed db Completed!"

''' Execute the program immediately '''
scraper_runner(scraper_main(scraper_builder(), string_parser()),AirTable_connector=AirTable_Connector())




