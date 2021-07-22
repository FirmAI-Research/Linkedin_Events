#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#author: Tarek R.
#date: Jul 12, 2021

from custom import prepareCookies, EvaluateIfWeAreInLastPage, GetTargetDirectory, GetTargetFile,SortListByDicionaryKeyValue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
import time
import re
import os
import csv
import pandas as pd
from random import randint as rand

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches",["enable-automation",'enable-logging'])
options.add_argument('--ignore-certificate-errors')


def GetEventInfo(driver):
    EventName = driver.find_element_by_xpath('//div[@class="events-top-card__info-container"]/h1').text
    
    return EventName
   

def checkIfAlreadyJoinedTheEvent(driver):
    time.sleep(4)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//button')))
    except:
        pass
    try:
        attendButton = driver.find_element_by_xpath('//div[contains(@class,"events-social-card-header")]/button')
    except:
        return 'Already a Member'
    attendButtonID = attendButton.get_attribute("id")
    status = driver.execute_script(f'return document.getElementById("{attendButtonID}").innerText;')
    if status == 'Invite connections':
        print('Already attended the event..')
        return 'Already a Member'
    else:
        print('This is a new event, trying to join......')
        return 'New Event'


def joinEvent(driver):
    print('Waiting to click join button')
    attendButton = driver.find_element_by_xpath('//div[@class="events-social-card-header__cta"]/button')
    #WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, attendButton.get_attribute("id"))))
    try:
        time.sleep(rand(2,5))
        driver.execute_script(f'document.getElementById("{attendButton.get_attribute("id")}").click()')
        time.sleep(rand(4,7))
        print('Successfully Joined THe Event')
        driver.execute_script("document.getElementsByClassName('lead-gen-modal__submit-button artdeco-button artdeco-button--2')[0].click()")
    except:
        pass

def GetTotalAttendees(driver):
    WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, '//ul[@tabindex]/..//span')))
    TotalAttendees = driver.execute_script('return document.getElementsByClassName("events-live-social-proof__copy-text t-14")[0].innerText')
    return re.sub(r' .+','',TotalAttendees)



def ListEachPagesResult(driver):
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="entity-result__item"]')))
        ParentBoxOfEachProfiles = driver.find_elements_by_xpath('//div[@class="entity-result__item"]') #list
        return ParentBoxOfEachProfiles
    except:
        return 0

# parameters: eachbox
def EvaluateProfileNameVisibility(eachBox):
    try:
        NameOfEachProfile = eachBox.find_element_by_xpath('.//span[@dir="ltr"]/span').text
        return NameOfEachProfile
    except:
        return 0

# parameters: eachBox
def GetName(eachBox):
    Test = EvaluateProfileNameVisibility(eachBox)
    if Test==0:
        print('Name Not Visble')
        Name = 'LinkedIn Member'
        return Name
    else:
        Name = Test
        print(f'Name Visible: {Name}')
        return Name

# parameters: eachBox
def EvaluatePositionAndCompany(eachBox):
    try:
        PositionAndCompany = eachBox.find_element_by_xpath('.//div[@class="linked-area flex-1 cursor-pointer"]//div[contains(@class,"primary")]').text
        print(PositionAndCompany)
        return PositionAndCompany
    except:
        return 0

# parameters: eachBox
def GetPositionAndCompany(eachBox):
    Test = EvaluatePositionAndCompany(eachBox)
    if Test==0:
        PositionAndCompany = ''
    else:
        PositionAndCompany = Test
        return PositionAndCompany

def EvaluateLocationAvailability(eachBox):
    try:
        Location = eachBox.find_element_by_xpath('.//div[@class="linked-area flex-1 cursor-pointer"]//div[contains(@class,"secondary")]').text
        print(Location)
        return Location
    except:
        return 0

def GetLocation(eachBox):
    Test = EvaluateLocationAvailability(eachBox)
    if Test==0:
        Location = ''
    else:
        Location = Test
    return Location

def GetProfileURL(eachBox):
    ProfileURL = eachBox.find_element_by_xpath('.//span/a[@href]').get_attribute('href')
    if 'linkedin.com/in' in ProfileURL:
        return re.sub(r'\?.+','',ProfileURL)
    else:
        return ProfileURL


def EvaluateNextButtonVisibility(driver):
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="entity-result  "]')))
        NB = driver.find_elements_by_xpath('//*[@class="entity-result  "]')[-1]
        action = ActionChains(driver)
        NB.location_once_scrolled_into_view
        time.sleep(rand(2,5))
        action.move_to_element(NB).perform()
        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-current="true"]/../following-sibling::li[1]')))
        Test = driver.find_element_by_xpath('//button[@aria-current="true"]/../following-sibling::li[1]')
        print(f'Next Button Found: {Test}')
        NextButtonID=Test.get_attribute('id')
        return NextButtonID
    except:
        return 0


def ClickNextButton(driver):
    Test = EvaluateNextButtonVisibility(driver)
    if Test==0:
        return False
    else:
        driver.execute_script(f"document.getElementById('{Test}').firstElementChild.click()")
        print('Next Button Clicked... Waiting for Next pages result to be visible')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="entity-result  "]')))
        
def GetANZ_Attendees(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pb2 t-black--light t-14"]')))
        TotalANZ_Attendees = driver.find_element_by_xpath('//div[@class="pb2 t-black--light t-14"]').text
        
        return re.sub(r' .+','',TotalANZ_Attendees)
    except:
        return 0

def CheckIfEventEnded(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-inline-feedback__message')))
        return 'Ended'
    except:
        pass

def scrapEachPage(ALLDATA,ANZDATA,EventName,EventURL,TotalAttendees,driver):
    ScrapingTime = time.ctime()
    ParentBoxes = ListEachPagesResult(driver)
    ANZ_Atteendees = GetANZ_Attendees(driver)
    #WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//div[@class="entity-result__item"]')))
    if ParentBoxes == 0:
        FullName = ''
        PositionAndCompany = ''
        Location = ''
        ProfileURL = ''
        # get unique id
        data = {
            'Scraping Time': ScrapingTime,
            'Event URL':EventURL,
            'Event Name': EventName,
            'Total Attendees':TotalAttendees,
            'Total ANZ Atteendees': ANZ_Atteendees,
            'Full Name':FullName,
            'Position And Company':PositionAndCompany,
            'Location':Location,
            'Profile URL':ProfileURL
            }
        ALLDATA.append(data)
        ANZDATA.append(data)
    else:
        for eachBox in ParentBoxes:
            try:
                FullName = GetName(eachBox)
            except:
                FullName = ''
            try:
                PositionAndCompany = GetPositionAndCompany(eachBox)
            except:
                PositionAndCompany = ''
            try:
                Location = GetLocation(eachBox)
            except:
                Location = ''
            try:
                ProfileURL = GetProfileURL(eachBox)
            except:
                ProfileURL = ''
            # get unique id
            data = {
                'Scraping Time': ScrapingTime,
                'Event URL':EventURL,
                'Event Name': EventName,
                'Total Attendees':TotalAttendees,
                'Total ANZ Atteendees': ANZ_Atteendees,
                'Full Name':FullName,
                'Position And Company':PositionAndCompany,
                'Location':Location,
                'Profile URL':ProfileURL
                }
            ALLDATA.append(data)
            ANZDATA.append(data)

driver=webdriver.Chrome(options=options, executable_path='/home/ubuntu/Desktop/chromedriver')#'/home/tarek/my_Projects/chromedriver' #'/home/ubuntu/Desktop/chromedriver'

stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", fix_hairline=True,)
prepareCookies(driver)

def ScrapAttendees(EventURL,ANZDATA):
    ALLDATA = []
    EventID=str(re.sub(r'/.+|/$','',EventURL.replace('https://www.linkedin.com/events/','')))
    
    driver.get(EventURL)
    if CheckIfEventEnded(driver)!='Ended':
        check_event = checkIfAlreadyJoinedTheEvent(driver)
        EventName = GetEventInfo(driver)
        if check_event=='Already a Member':
            pass
        elif check_event=='New Event':
            try:
                joinEvent(driver)
            except:
                pass
        TotalAttendees = GetTotalAttendees(driver)
        
        a = EventURL.replace('https://www.linkedin.com/events/','').replace('/','')
        geocode='"101452733"%2C"105490917"'
        GeoEventURL = f'https://www.linkedin.com/search/results/people/?eventAttending="{a}"&geoUrn=%5B{geocode}%5D&origin=FACETED_SEARCH'
        driver.get(GeoEventURL)
        while True:
            scrapEachPage(ALLDATA,ANZDATA,EventName,EventURL,TotalAttendees,driver)
            time.sleep(rand(4,15))
            LastPageTest = EvaluateIfWeAreInLastPage(driver)
            
            if LastPageTest==True:
                break
            else:
                pass
            action = ClickNextButton(driver)
            if action==False:
                break
            else:
                pass
        
        ParentFolder = 'Database Backup'
        
        characters = ['/']
        for i in characters:
            EventName = EventName.replace(i,'-')
        
        SubFolder = EventName
        
        try:
            os.mkdir(os.path.join(ParentFolder,SubFolder))
        except:
            pass
        FileName = (f'{SubFolder} {EventID} at {time.ctime()}.csv')
        CSV_ExportFileName = os.path.join(ParentFolder,SubFolder,FileName)
        
        fieldnames = ALLDATA[0].keys()
        with open(CSV_ExportFileName,'w',  encoding="utf8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            writer.writerows(ALLDATA)
            csvfile.close()
        #print(f'"{FileName}" has been successfully created')
    else:
        pass


def main():
    userInput = input('Type 1 to Continue with a CSV file\nType 2 to scrap a single events attendees\n>>>>>>>>> : ')
    if userInput=='1':
        csvfile = GetTargetFile('Select input CSV file (with column name "URL"')
        ParentFolder = 'Event Database'
        SubFolder = re.sub(r'/(.+)','',(re.sub(r'.+Database/','',csvfile)))
        try:
            os.mkdir(os.path.join(ParentFolder,SubFolder,'ANZ Attendees'))
        except:
            pass
        
        with open(csvfile, 'r', encoding="utf8") as inputCSV:
            reader = csv.DictReader(inputCSV,delimiter=",")
            events = []
            for row in reader:
                events.append(row)
        ANZDATA = []
        try:
            for i in events:
                if int(i['EventAttendees'])>20:
                    ScrapAttendees(i['EventURL'],ANZDATA)
                    time.sleep(rand(3,10))
                else:
                    pass
        finally:
            df = pd.DataFrame(ANZDATA)
            try:
                df[["First Name","Last Name"]] = ''
                for i in range(len(df)):
                    FullName = df.loc[i, "Full Name"]
                    F = FullName.split(' ')
                    if len(F)==1:
                        df.loc[i, "First Name"]= F[0]
                        df.loc[i, "Last Name"]= ''
                    elif len(F)>1:
                        df.loc[i, "First Name"]= F[0]
                        df.loc[i, "Last Name"]= F[1]
                FileName = f'ANZ Attendees at {time.ctime()}.csv'
                df.to_csv(os.path.join(ParentFolder,SubFolder,'ANZ Attendees',FileName))
            except:
                FileName = f'ANZ Attendees at {time.ctime()}.csv'
                df.to_csv(os.path.join(ParentFolder,SubFolder,'ANZ Attendees',FileName))
                
    elif userInput=='2':
        eventURL = input('\nType the events url\n>>> : ')
        return ScrapAttendees(eventURL)

main()
driver.quit()