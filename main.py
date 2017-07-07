from job_board_scraper_framework import *
from GSheet_connect import *

print "job_board scraping starts... \n"

#build a scraper class
scraper_main = scraper_main(scraper_builder(),string_parser())

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

#store the data to google sheets (Option 1)
GSheet_connector = GSheet_connector()
GSheet_connector.processor(scraper_main.output)

#store the data to mysql (Option 2)
# mysqlObj = mysqlObj()
# mysqlObj.truncate_mysql_by_companies(scraper_main.companyNameList)
# mysqlObj.mysql_insert(scraper_main.output)
# mysqlObj.mysql_close()

print "\n import to Google Sheet Completed!"

