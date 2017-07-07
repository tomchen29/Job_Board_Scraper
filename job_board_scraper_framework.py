import urllib2
from bs4 import BeautifulSoup
import MySQLdb
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from geopy.geocoders import Nominatim

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

class scraper_builder():
    def soup_builder(self,url):
        return  BeautifulSoup(urllib2.urlopen(url, timeout = 15), "lxml")

    # without proxy set-up. Needs to change the exe path
    def selinum_buider(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )
        return webdriver.PhantomJS("phantomjs/bin/phantomjs.exe", desired_capabilities=dcap)

class string_parser():
    def location_cleaner(self,location):
        if not location or location =="":
            return ""
        if "," not in location:
            try:
                geolocator = Nominatim()
                long_location = (geolocator.geocode(location)).address
                location = (location+long_location[long_location.rfind(','):]).upper()
            except AttributeError:
                pass
        location = location.encode('ascii', 'ignore').decode('ascii')
        return location.upper()


class scraper_main():
    def __init__(self,scraper_builder, str_parser):
        self.companyNameList = []
        self.output = []
        self.scrap_builder = scraper_builder
        self.str_parser = str_parser

    ''' BeautifulSoup Scrapers  '''
    def starship_scraper(self):
        # target career page
        companyName = "Starship"
        self.companyNameList.append(companyName)
        job_link = "https://www.starship.xyz/careers/"

        #build a scraper
        soup = self.scrap_builder.soup_builder(job_link)

        #locate the starship job board
        job_board = soup.find(name="div",class_= "newslist" )

        #output:[(company_name, job_title, job_location, job_url, job_date)]
        for dateTime in job_board.find_all("span"):
            jobTitle = dateTime.next_sibling.text
            if jobTitle == "":
                continue

            job_detail_url = dateTime.next_sibling['href']

            postDate = dateTime.text

            try:
                detail_soup = self.scrap_builder.soup_builder(job_detail_url)

                ulEles = detail_soup.find_all("ul", class_="careers")
                terms_ele = ulEles[len(ulEles) - 1]
                location = terms_ele.text

                if 'Location:' in location:
                    location = location[(location.index('Location:') + 10):]
                    location = location[:location.index('\n')]
                elif 'Location' in location:
                    location = location[(location.index('Location') + 9):]
                    alphaIndex = -1
                    for i in range(len(location)):
                        if location[i].isalpha():
                            alphaIndex = i
                            break
                    location = location[alphaIndex:location.index('\n')]
                else:
                    if not jobTitle.index(",") >0:
                        raise ValueError('title does not contain location: '+job_detail_url)
                    else:
                        location = jobTitle[jobTitle.index(",") +2 :]
                        if not location[0].isupper():
                            raise ValueError('location scraped from title is wrong: ' + job_detail_url)
                location = self.str_parser.location_cleaner(location)
                #append as a tuple
                self.output.append((companyName, jobTitle, job_detail_url, postDate,location))
            except TypeError:
                continue
            except IndexError:
                print job_detail_url

    def vida_scraper(self):
        # target career page
        companyName = "Vida"
        self.companyNameList.append(companyName)
        job_link = "https://shopvida.com/pages/careers"

        #build a scraper
        soup = self.scrap_builder.soup_builder(job_link)

        #locate the starship job board
        job_board = soup.find("div", class_="positions-wrapper")
        job_board = job_board.find_all(name="div",class_= "position" )

        #output:[(company_name, job_title, job_location, job_url, job_date)]
        for jobObj in job_board:

            jobTitle = jobObj.find("h4").text
            if jobTitle == "":
                continue
            sub_url = str(jobObj.find("a")['href'])
            if sub_url.startswith("http"):
                continue
            job_detail_url = "https://shopvida.com"+sub_url
            postDate = ""

            try:
                detail_soup = self.scrap_builder.soup_builder(job_detail_url)

                textBlock = str(detail_soup.find("section", id="content"))

                if "<h4><strong>LOCATION</strong></h4>" in textBlock:
                    locationIndex = textBlock.index("<h4><strong>LOCATION</strong></h4>")
                    location = textBlock[locationIndex + 33:]
                    location = location[location.index("<p>") + 3:location.index("</")]
                elif "<b>LOCATION</b>" in textBlock:
                    locationTagIndex = textBlock.index("<b>LOCATION</b>")
                    location = textBlock[locationTagIndex + 16:]
                    location = location[location.index("<span")+4:]
                    location = location[location.index(">")+1:location.index("<")]
                else:
                    location = ""
                location = self.str_parser.location_cleaner(location)

                #append as a tuple
                self.output.append((companyName, jobTitle, job_detail_url, postDate, location))
            except TypeError:
                continue
            except IndexError:
                print job_detail_url

    def voiq_scraper(self):
        # target career page
        companyName = "Voiq"
        self.companyNameList.append(companyName)
        job_link = "https://voiq.breezy.hr/"

        #build a scraper
        soup = self.scrap_builder.soup_builder(job_link)

        #locate the starship job board
        job_board = soup.find("ul", class_="positions")

        #output:[(company_name, job_title, job_location, job_url, job_date)]
        for jobObj in job_board.find_all("li"):
            if 'position' not in jobObj['class']:
                continue
            jobTab = jobObj.find("a")
            jobTitle = jobTab.find("h2").text
            if jobTitle == "":
                continue
            job_detail_url = "http://voiq.breezy.hr"+jobTab['href']
            postDate = ""

            location = (jobObj.find("li", class_="location").find("span")).text
            location = self.str_parser.location_cleaner(location)

            # append as a tuple
            self.output.append((companyName, jobTitle, job_detail_url, postDate, location))

    ''' Selenium Scrapers  '''
    # No location on website ,default "LOS ANGELES, CA"
    def socialnative_scraper(self):
        # target career page
        companyName = "Social Native"
        self.companyNameList.append(companyName)
        job_link = "http://www.socialnative.com/jobs/"

        # build a scraper
        driver = self.scrap_builder.selinum_buider()
        driver.implicitly_wait(0.5)  # wait for 0.5 second when trying to find an element in case it's not immediately available.
        driver.get(job_link)

        bodyElement = driver.find_element_by_tag_name('body')
        jobTitles = bodyElement.find_elements_by_css_selector('div.card-body h2')
        urls = [x.get_attribute("href") for x in bodyElement.find_elements_by_css_selector('div.card-post-body a')]

        # output:[(company_name, job_title, job_location, job_url, job_date)]
        for i in range(len(jobTitles)):
            jobTitle = (jobTitles[i]).text
            job_detail_url = urls[i]
            postDate = ""
            location = "LOS ANGELES, CA"
            location = self.str_parser.location_cleaner(location)

            # append as a tuple
            self.output.append((companyName, jobTitle, job_detail_url, postDate, location))

        driver.close()

    def regalii_scraper(self):
        # target career page
        companyName = "Regalii"
        self.companyNameList.append(companyName)
        job_link = "https://www.regalii.com/careers/"

        # build a scraper
        driver = self.scrap_builder.selinum_buider()
        driver.implicitly_wait(0.5)  # wait for 0.5 second when trying to find an element in case it's not immediately available.
        driver.get(job_link)

        bodyElement = driver.find_element_by_tag_name('body')
        jobTitles = bodyElement.find_elements_by_css_selector('ul.fancy li a')
        urls = [x.get_attribute("href") for x in jobTitles]

        # output:[(company_name, job_title, job_location, job_url, job_date)]
        for i in range(len(jobTitles)):
            titleLocCombo = (jobTitles[i]).text
            jobTitle = titleLocCombo[:titleLocCombo.index(",")]
            job_detail_url = urls[i]
            postDate = ""
            location = titleLocCombo[titleLocCombo.index(",")+2:]
            location = self.str_parser.location_cleaner(location)

            # append as a tuple
            self.output.append((companyName, jobTitle, job_detail_url, postDate, location))
        driver.close()

    ''' Unreal scraper'''
    def yup_scraper(self):
        companyName = "Yup"
        self.companyNameList.append(companyName)
        # output:[(company_name, job_title, job_location, job_url, job_date)]
        self.output.append((companyName, "*Multiple Positions", "https://www.yup.com/who-we-are", "", "SAN FRANCISCO, CA"))











