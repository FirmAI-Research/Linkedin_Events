#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#author: Tarek R.
#date: Jul 12, 2021

from pandas.core.frame import DataFrame
from custom import prepareCookies, EvaluateIfWeAreInLastPage, GetTargetFile, GetUserInputViaPrompt, CallDateTime, SearchEvents
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
from datetime import datetime
from datetime import date
pd.options.mode.chained_assignment = None

class USER_INPUTS:
    def Startup_Mandatory_Inputs():
        csvfile = GetTargetFile('Select input CSV file (with column name')
        exit() if not isinstance(csvfile, str) else print(csvfile)
        minimumAttendessRequired = GetUserInputViaPrompt('Minimum Attendees Requirement','Shall we skip events with less than 10 going?\nType Y/N')
        exit() if minimumAttendessRequired=='' or minimumAttendessRequired==None or isinstance(minimumAttendessRequired, tuple) else print(minimumAttendessRequired)
        Match_Keywords_with_EventTitle_and_Description = GetUserInputViaPrompt('Match Keywords with Title & Description','What keywords shall we scrape events for in the description / title?\nSeparate Keywords by comma\n - Leave blank if you want to scrape all')
        exit() if isinstance(Match_Keywords_with_EventTitle_and_Description, tuple) else print(Match_Keywords_with_EventTitle_and_Description)
        return csvfile,minimumAttendessRequired,Match_Keywords_with_EventTitle_and_Description
    def DelayRange():
        lowest = int(GetUserInputViaPrompt('Delay Setting For Profile Visiting','Lowest Delay in Second'))
        highest = int(GetUserInputViaPrompt('Delay Setting For Profile Visiting','Highest Delay in Second'))
        delay_time_range_when_browsing_profiles=(lowest,highest)
        return delay_time_range_when_browsing_profiles
    def paginationDelay():
        lowest = int(GetUserInputViaPrompt('Delay Setting For Even Attendees List Pagination','Lowest Delay in Second'))
        highest = int(GetUserInputViaPrompt('Delay Setting For Even Attendees List Pagination','Highest Delay in Second'))
        delay_time_range_when_paginating_attendee_list=(lowest,highest)
        return delay_time_range_when_paginating_attendee_list

class PERSONAL_PROFILE:
    def test_company_info_style(driver):
        try:
            driver.find_element_by_xpath('//span[text()="Company Name"]/following-sibling::span/ancestor-or-self::section[contains(@class,"pv-position-entity") and //*[contains(text(),"Present")]]')    
            return True
        except:
            return False
    def get_company_name(driver):
        if PERSONAL_PROFILE.test_company_info_style(driver) == True:
            return driver.find_element_by_xpath('//span[text()="Company Name"]/following-sibling::span').text
        else:
            try:
                Company = driver.find_element_by_xpath('//section[@id="experience-section"]/ul[contains(@class,"pv-profile-section__")]/li//p[2]').text
            except:
                Company = None
            return Company
    def get_company_linkedin_url(driver):
        if PERSONAL_PROFILE.test_company_info_style(driver) == True:
            return driver.find_element_by_xpath('//span[text()="Company Name"]/following-sibling::span/ancestor-or-self::section[contains(@class,"pv-position-entity")]//a').get_attribute('href')
        else:
            try:
                Company_LinkedInURL = driver.find_element_by_xpath('//section[@id="experience-section"]/ul[contains(@class,"pv-profile-section__")]/li//a').get_attribute('href')
            except:
                Company_LinkedInURL = None
            return Company_LinkedInURL
            
    def get_title(driver):
        if PERSONAL_PROFILE.test_company_info_style(driver) == True:
            return driver.find_element_by_xpath('//div[contains(@class,"role-details")]//h3/span[2]').text
        else:
            try:
                Title = driver.find_element_by_xpath('//section[@id="experience-section"]/ul[contains(@class,"pv-profile-section__")]/li//h3').text
            except:
                Title = None
            return Title

def StartDriver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches",["enable-automation",'enable-logging'])
    options.add_argument('--ignore-certificate-errors')
    driver=webdriver.Chrome(options=options, executable_path='/home/tarek/my_Projects $$ ****/chromedriver')#'/home/tarek/my_Projects $$ ****/chromedriver' #'/home/ubuntu/Desktop/chromedriver'
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", fix_hairline=True,)
    prepareCookies(driver)
    return driver

def DropDuplicates(DataFrame):
    ExportDict=DataFrame.drop_duplicates(subset ='Profile URL',keep = "first", inplace = False)
    return ExportDict

def ReIndex_Attendees_DataFrame(DataFrame:object):
    column_names = ['Scraping Time', 'EventURL', 'EventName', 'TotalAttendees', 'ANZ Atteendees', 'Position And Company', 'Location', 'Profile URL','Full Name','Total Events Attending', 'Title', 'Company', 'First Name', 'Last Name','Company Name','Position','Company LinkedIn URL']
    df = DataFrame.reindex(columns=column_names)
    return df

def Cleanup_EventsDashboard_Output(outDict_of_EventsDashboard:list,FilteredDict:list):
    ExportDict = CalculateAttendeeGrowth(outDict_of_EventsDashboard,FilteredDict)
    return ExportDict

def ReIndex_Summary_DataFrame(DataFrame:object):
    column_names = ['Scraping Time', 'EventURL', 'EventName', 'TotalAttendees', 'PreviousAttendees', 'Total Growth', 'ANZ Atteendees', 'Event Description', 'Event Date','Beginning Day','Finishing Day', 'Days_from_Begining_Day', 'Days_from_Finishing_Day']
    df = DataFrame.reindex(columns=column_names)
    return df

def Split_Fullname_and_Company(Dic):
    df = pd.DataFrame(Dic)
    df[["First Name","Last Name"]] = ''
    df[["Title","Company"]] = ''
    for i in range(len(df)):
        if df.loc[i, "Full Name"]==None:
            pass
        else:
            FullName = df.loc[i, "Full Name"]
            F = FullName.split(' ')
            if len(F)==1:
                df.loc[i, "First Name"]= F[0]
                df.loc[i, "Last Name"]= None
            elif len(F)>1:
                df.loc[i, "First Name"]= F[0]
                df.loc[i, "Last Name"]= F[1]
            Position_And_Company = df.loc[i, 'Position And Company']
            if ' at ' in Position_And_Company:
                PC = Position_And_Company.split(' at ')
                df.loc[i, "Title"] = PC[0]
                df.loc[i, "Company"] = PC[1]
            else:
                df.loc[i, "Title"] = None
                df.loc[i, "Company"] = None
    return df

def ReadInputCSV(csvfile):
    with open(csvfile, 'r', encoding="utf8") as inputCSV:
        reader = csv.DictReader(inputCSV,delimiter=",")
        events = []
        for row in reader:
            events.append(row)
        inputCSV.close()
    return events

def GetEventName(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//h1[contains(@class,"title")]')))
    EventName = driver.find_element_by_xpath('//h1[contains(@class,"title")]').text
    return EventName

def checkIfAlreadyJoinedTheEvent(driver):
    time.sleep(4)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//button')))
    except:
        pass
    try:
        driver.find_element_by_xpath('//div[contains(@class,"events-social-card-header")]/button').click()
    except:
        pass
    time.sleep(rand(4,7))
    try:
        driver.execute_script("document.getElementsByClassName('lead-gen-modal__submit-button artdeco-button artdeco-button--2')[0].click()")
    except:
        pass

def GetTotalAttendees(driver):
    try:
    	WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.CLASS_NAME, '//span[contains(@class,"social-proof")]')))
    except:
    	pass
    try:
        TotalAttendees = driver.execute_script('return document.getElementsByClassName("events-live-social-proof__copy-text t-14")[0].innerText')
        T = TotalAttendees.replace(',','')
        totalAttendees = re.search(r'\d+',T)
        return int(totalAttendees.group())
    except:
    	return 'Error Occured'

def GetANZ_Attendees(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="pb2 t-black--light t-14"]')))
        TotalANZ_Attendees = driver.find_element_by_xpath('//div[@class="pb2 t-black--light t-14"]').text
        T = TotalANZ_Attendees.replace(',','')
        totalANZAttendees = re.search(r'\d+',T)
        return int(totalANZAttendees.group())
    except:
        return 0

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
        PositionAndCompany = eachBox.find_element_by_xpath('.//div[contains(@class,"entity-result__primary-subtitle")]').text
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
        Location = eachBox.find_element_by_xpath('.//div[contains(@class,"entity-result__secondary")]').text
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
        WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.XPATH, '//span/a[@href]')))
        NB = driver.find_elements_by_xpath('//span/a[@href]')[-1]
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
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.XPATH, '//span/a[@href]')))

def CheckIfEventEnded(driver):
    try:
        driver.refresh()
        time.sleep(rand(1,3))
        t =rand(2,3)
        driver.execute_script(f"window.scrollBy(0,document.body.scrollHeight/{t})")
        time.sleep(rand(1,3))
        driver.execute_script(f"window.scrollBy(0,document.body.scrollHeight/{t})")
        driver.find_element_by_xpath('//span[text()="Event ended"]')
        print('Ended')
        return 'Ended'
    except:
        print('Not-Ended')
        return 'Not-Ended'

def match(TitlePlusDesc,Keywords):
    for each_keyword in Keywords:
        each_keyword = re.sub(r'^ ',"",each_keyword)
        if each_keyword.lower() in TitlePlusDesc.lower():
            return True
    return False

'''
def main():
    ParentFolder = 'Event Database'
    SubFolder = re.sub(r'/(.+)','',(re.sub(r'.+Database/','',csvfile)))
    try:
        os.mkdir(os.path.join(ParentFolder,SubFolder,'ANZ Attendees'))
    except:
        pass
    
    events = GetEventName(csvfile)

    
    finally:
        df = Split_Fullname_and_Company(ANZDATA)
        FileName = f'ANZ Attendees (From Scrap Attendees Run at {time.ctime()}).csv'
        df.to_csv(os.path.join(ParentFolder,SubFolder,'ANZ Attendees',FileName))
    '''

def GetPreviousAttendees(EventURL,OldDatasetList):
    for o in OldDatasetList:
        if EventURL==o['EventURL']:
            return o['TotalAttendees']

def CalculateAttendeeGrowth(LatestDataSetList:list,OldDatasetList:list):
    NewDataDictList = []
    for j in LatestDataSetList:
        j['PreviousAttendees'] = GetPreviousAttendees(j['EventURL'],OldDatasetList)
        j['Total Growth'] = int(j['TotalAttendees']) - int(j['PreviousAttendees'])
        NewDataDictList.append(j)
    return NewDataDictList

def GenerateANZattendeesLink(EventURL):
    a = EventURL.replace('https://www.linkedin.com/events/','').replace('/','')
    ANZgeocode = '"101452733"%2C"105490917"'
    USAgeocode = '"103644278"'
    GeoEventURL = f'https://www.linkedin.com/search/results/people/?eventAttending="{a}"&geoUrn=%5B{USAgeocode}%5D&origin=FACETED_SEARCH'
    return GeoEventURL

def EventFrontPage(EventURL, driver):
    driver.get(EventURL)
    time.sleep(rand(3, 6))
    EventName = GetEventName(driver)
    print(EventName)
    TotalAttendees = GetTotalAttendees(driver)
    Event_Date = driver.find_element_by_xpath('//div[*[@type="calendar-icon"]]//span').text
    try:
        checkIfAlreadyJoinedTheEvent(driver)
    except:
        print(f"debugger4: checkIfAlreadyJoinedTheEvent")
    Output = {'EventURL':EventURL,'EventName':EventName,'TotalAttendees':TotalAttendees,'Event Date':Event_Date}
    return Output



def ScrapEachProfileFromAttendeesList(EachBox):      
    FullName = GetName(EachBox)
    PositionAndCompany = GetPositionAndCompany(EachBox)
    Location = GetLocation(EachBox)
    ProfileURL = GetProfileURL(EachBox)
    data = {
        'Scraping Time': time.ctime(),
        'Full Name':FullName,
        'Position And Company':PositionAndCompany,
        'Location':Location,
        'Profile URL':ProfileURL
        }
    print(f"Debugger3:\n {data}")
    return data

def EachPageOfEventANZattendeesScrap(driver):
    ParentBoxes = ListEachPagesResult(driver)
    result =[]
    if isinstance(ParentBoxes, list):
        time.sleep(rand(3,6))
        for eachBox in range(len(ParentBoxes)):
            INFO = ScrapEachProfileFromAttendeesList(ParentBoxes[eachBox])
            result.append(INFO)
    elif ParentBoxes==0:
        result.append({
        'Scraping Time': time.ctime(),
        'Full Name':None,
        'Position And Company':None,
        'Location':None,
        'Profile URL':None
        })
    return result


def ProceedToAttendeeScrap(driver,EventURL,paginationDelay:tuple):   
    AllAttendeesofThisEvent = []
    IsEnded = CheckIfEventEnded(driver)
    if IsEnded=='Not-Ended':
        ANZattendeesLink =GenerateANZattendeesLink(EventURL)
        driver.get(ANZattendeesLink)
        time.sleep(rand(1,3))
        TotalANZ_Atteendees = GetANZ_Attendees(driver)
        while True:
            ANZ_Atteendees = EachPageOfEventANZattendeesScrap(driver)
            [AllAttendeesofThisEvent.append(ANZ_Atteendee) for ANZ_Atteendee in ANZ_Atteendees]
            time.sleep(rand(paginationDelay[0],paginationDelay[1]))
            if EvaluateIfWeAreInLastPage(driver)==True or ClickNextButton(driver)==False:
                break
        [i.update({'ANZ Atteendees':TotalANZ_Atteendees}) for i in AllAttendeesofThisEvent]
    elif IsEnded=='Ended':
        AllAttendeesofThisEvent.append({
        'Scraping Time': time.ctime(),
        'ANZ Atteendees':None,
        'Full Name':None,
        'Position And Company':None,
        'Location':None,
        'Profile URL':None})
    else:
        AllAttendeesofThisEvent.append({
        'Scraping Time': time.ctime(),
        'ANZ Atteendees':None,
        'Full Name':None,
        'Position And Company':None,
        'Location':None,
        'Profile URL':None})
    return AllAttendeesofThisEvent


def CountDuplicates(ProfileURL,DataFrame):
    count=0
    if ProfileURL==None or 'headless' in ProfileURL:
        return None
    for i in range(len(DataFrame)):
        if DataFrame.loc[i, 'Profile URL'] == None:
            pass
        elif DataFrame.loc[i, 'Profile URL'] == ProfileURL:
            count=count+1
    return count

def addDuplicateOccurance(DataFrame):
    DataFrame[['Total Events Attending']] = None
    for i in range(len(DataFrame)):
        DataFrame.loc[i, 'Total Events Attending']=CountDuplicates(DataFrame.loc[i, 'Profile URL'],DataFrame)
    return DataFrame

def EvaluateMatchingKeywords(Match_Keywords_with_EventTitle_and_Description:str):
    if not ',' in Match_Keywords_with_EventTitle_and_Description:
        Keywords = [Match_Keywords_with_EventTitle_and_Description,Match_Keywords_with_EventTitle_and_Description]
    elif ',' in Match_Keywords_with_EventTitle_and_Description:
        Keywords = Match_Keywords_with_EventTitle_and_Description.split(',')
    return Keywords

def scroll_to_last_script(driver):
    driver.execute_script('window.scrollBy(0,document.body.scrollHeight)')

def scroll_to_middle(driver):
    driver.execute_script('window.scrollTo(0,document.body.scrollHeight/3)')

def scroll_to_fast(driver):
    driver.execute_script('window.scrollTo(0,0)')
def visitProfile(driver, url:str):
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//h2')))
    except:
        pass
    time.sleep(rand(3,10))
    scroll_to_last_script(driver)
    time.sleep(rand(2,12))
    scroll_to_middle(driver)
    time.sleep(rand(4,12))
    o = GetCompanyAndTitle(driver)
    return o


def GetCompanyAndTitle(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//a[contains(@data-control-name,"company")]//h3/following-sibling::p[2]')))
    except:
        pass
    
    Company = PERSONAL_PROFILE.get_company_name(driver)
    Company_LinkedInURL = PERSONAL_PROFILE.get_company_linkedin_url(driver)
    Title = PERSONAL_PROFILE.get_title(driver)
    output = {'Company Name':Company,'Company LinkedIn URL':Company_LinkedInURL,'Position':Title}
    return output

def Crawl_Individuals(driver,AttendeesDict,pro_scraping_timing:tuple):
    list=[]
    Profiles = AttendeesDict
    for  profile in Profiles:
        print(profile['Profile URL'])
        if profile['Profile URL']==None or "headless" in profile['Profile URL']:
            list.append({'Company Name':None,'Company LinkedIn URL':None,'Position':None})
        else:
            ProfileInfo = visitProfile(driver, str(profile['Profile URL']))
            time.sleep(rand(pro_scraping_timing[0],pro_scraping_timing[1]))
            print(ProfileInfo)
            list.append(ProfileInfo)
    return list


def InitiateAttendeeCollection():
    csvfile,minimumAttendessRequired,Match_Keywords_with_EventTitle_and_Description = USER_INPUTS.Startup_Mandatory_Inputs()
    
    EventsInImportedCSV = ReadInputCSV(csvfile)
    print(EventsInImportedCSV[0].items())
    ImportDF = pd.DataFrame(EventsInImportedCSV)
    if minimumAttendessRequired=='Y':
        DF = ImportDF.loc[ImportDF['TotalAttendees'].astype(int) > 10]
    elif  minimumAttendessRequired == 'N':
        DF = ImportDF
    else:
        exit()
    if Match_Keywords_with_EventTitle_and_Description!='':
        DF = DF[(DF['EventTitle'].str.contains('|'.join(EvaluateMatchingKeywords(Match_Keywords_with_EventTitle_and_Description)))) | (DF['EventShortDesc'].str.contains('|'.join(EvaluateMatchingKeywords(Match_Keywords_with_EventTitle_and_Description))))]
        DF[["Keywords Match"]] = 'True'
    else:
        pass
    FilteredDict = DF.to_dict('records')
    return FilteredDict

def StartCrawl(driver,FilteredDict,paginationDelay):
    outDict_of_EventsDashboard=[]
    outDict_of_Attendees=[]
    N=[]
    for Event in FilteredDict:
        FrontPageObjects = EventFrontPage(Event['EventURL'], driver)
        print(f"\nDebug:::\n FrontPageObjects:\n {FrontPageObjects}")
        ANZ_AttendeesObjects = ProceedToAttendeeScrap(driver,Event['EventURL'],paginationDelay)
        print(f"\nDebug::: ANZ_AttendeesObjects Length: {len(ANZ_AttendeesObjects)}")
        print(f"\nDebug:::\n ANZ_AttendeesObjects items in first dict: {ANZ_AttendeesObjects[0].items()}")
        FrontPageObjects.update({'Scraping Time':time.ctime(),'ANZ Atteendees':ANZ_AttendeesObjects[0]['ANZ Atteendees'],'Event Description':Event['EventShortDesc']})
        FrontPageObjects.update(CallDateTime(FrontPageObjects['Event Date']))
        #[each_dict.update(FrontPageObjects) for each_dict in ANZ_AttendeesObjects]
        
        for each_dict in ANZ_AttendeesObjects:
            creating_newdict={**FrontPageObjects,**each_dict}
            N.append(creating_newdict)
        print(f"\nDebug:::\n After updating ANZ_AttendeesObjects:\n {N}")
        outDict_of_EventsDashboard.append(FrontPageObjects)
        #[outDict_of_Attendees.append(k) for k in ANZ_AttendeesObjects]
    return outDict_of_EventsDashboard,N#outDict_of_Attendees


def ScrapAttendees(pro_scraping_timing,paginationDelay):
    FilteredDict = InitiateAttendeeCollection()
    driver = StartDriver()
    outDict_of_EventsDashboard,outDict_of_Attendees = StartCrawl(driver,FilteredDict,paginationDelay)
    SummaryExportDict = CalculateAttendeeGrowth(outDict_of_EventsDashboard,FilteredDict)
    Z = ReIndex_Summary_DataFrame(pd.DataFrame(SummaryExportDict))
    Z.to_csv('test_export_of_summary.csv')

    Step =pd.DataFrame(outDict_of_Attendees)
    Step.to_csv('Before Personal Profile Scrap Starting.csv')
    Step0 = addDuplicateOccurance(Step)
    Step1 = DropDuplicates(Step0)
    Step1.to_csv('After deduping.csv')
    Step2 = Split_Fullname_and_Company(Step1.to_dict('records'))
    Step2.to_csv('After name splitting.csv')
    
    K = Step2.to_dict('records')
    PersonalProfileGather = Crawl_Individuals(driver,K,pro_scraping_timing)
    i=0
    for i in range(len(K)):
        K[i].update(PersonalProfileGather[i])
        i+=1
    X = ReIndex_Attendees_DataFrame(pd.DataFrame(K))
    X.to_csv('test_export_of_attendees.csv')
    
    driver.quit()


if __name__=='__main__':
    functions=GetUserInputViaPrompt('What do you want to do?',"1 -- SearchEvents\n2 -- Scrap Attendees\n\tType 1 or 2:: ")
    pro_scraping_timing = USER_INPUTS.DelayRange()
    paginationDelay=USER_INPUTS.paginationDelay()
    if functions=='1':
        SearchEvents()
    elif functions=='2':
        ScrapAttendees(pro_scraping_timing,paginationDelay)
    else:
        exit()
