#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#author: Tarek R.
#date: Jul 13, 2021

from custom import prepareCookies, EvaluateIfWeAreInLastPage, GetTargetDirectory, GetTargetFile, GetUserInputViaPrompt, SortListByDicionaryKeyValue
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import re
import os
import csv
import time
import pathlib
from random import randint as rand
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches",["enable-automation","enable-logging"])
options.add_argument('--ignore-certificate-errors')



def GeneratesearchURL(UserInput):
    PrefixOfEventSearchLink = 'https://www.linkedin.com/search/results/events/?keywords='
    EventQueryString = str(UserInput)
    URL = PrefixOfEventSearchLink + urllib.parse.quote(EventQueryString)
    return URL

def ListEachPagesEvents(driver):
    print('Waiting for Results to be visible')
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//li//*[@class="app-aware-link" and not(@aria-hidden)]')))
    ParentBoxOfEachEvents = driver.find_elements_by_xpath('//li[@class="reusable-search__result-container "]') #list
    print("Results are visible now")
    return ParentBoxOfEachEvents

def GetEventTitle(eachEvent):
    EventTitle = eachEvent.find_element_by_xpath('.//*[@class="app-aware-link" and not(@aria-hidden)]').text
    print(EventTitle)
    return EventTitle

def GetEventURL(eachEvent):
    EventURL = eachEvent.find_element_by_xpath('.//*[@class="app-aware-link" and not(@aria-hidden)]').get_attribute('href')
    print(EventURL)
    return EventURL

def GetEventAttendees(eachEvent,driver):
    data = driver.execute_script(f'return document.querySelectorAll("div.entity-result__simple-insight-text-container > span")[{eachEvent}].innerText')
    EventAttendees = int(re.sub(r' .+','',data).replace(',',''))
    print(EventAttendees)
    return EventAttendees

def GetEventDate(eachEvent,driver):
    EventDate = driver.execute_script(f'return document.querySelectorAll("div > div.entity-result__primary-subtitle.t-14.t-black")[{eachEvent}].innerText')
    print(EventDate)
    return EventDate

def GetEventShortDescription(eachEvent):
    EventShortDesc = eachEvent.find_element_by_xpath('.//p').text
    #print(EventShortDesc)
    return EventShortDesc

def scrapeEachResultPage(EventsDatabase,driver):
    ParentBoxes = ListEachPagesEvents(driver)
    ScrapingTime = time.ctime()
    for eachEvent in ParentBoxes:
        eachEventIndex = ParentBoxes.index(eachEvent)
        EventTitle = GetEventTitle(eachEvent)
        EventAttendees = GetEventAttendees(eachEventIndex,driver)
        EventDate = GetEventDate(eachEventIndex,driver)
        EventURL = GetEventURL(eachEvent)
        EventShortDesc = GetEventShortDescription(eachEvent)
        EventID=str(re.sub(r'/.+|/$','',EventURL.replace('https://www.linkedin.com/events/','')))
        data = {
            'ScrapingTime': ScrapingTime,
            'EventID':str(EventID),
            'EventTitle':EventTitle,
            'EventAttendees':int(EventAttendees),
            'EventDate':EventDate,
            'EventURL':EventURL,
            'EventShortDesc':str(EventShortDesc)
            }
        EventsDatabase.append(data)

def EventSearchPagination(driver):
    try:
        time.sleep(rand(1,3))
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'reusable-search__result-container ')))
        driver.execute_script('l = document.getElementsByClassName("reusable-search__result-container ");l[(l.length)-1].scrollIntoView();')
        time.sleep(rand(1,3))
        NextButtonID = driver.find_element_by_xpath('//button[@aria-current="true"]/../following-sibling::li[1]').get_attribute('id')
        driver.execute_script(f"a=document.getElementById('{NextButtonID}');a.firstElementChild.click()")
        return True
    except:
        print('Next Button not clickable\nPagination finished')
        return False

def SearchEventForEachKeyword(Each_Keyword):
    EventsDatabase = []
    EventSearchKeywordURL = GeneratesearchURL(Each_Keyword)
    driver=webdriver.Chrome(options=options, executable_path='/home/ubuntu/Desktop/chromedriver')#'/home/tarek/my_Projects/chromedriver'/home/ubuntu/Desktop/chromedriver
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", fix_hairline=True,)
    prepareCookies(driver)
    driver.get(EventSearchKeywordURL)
    while True:
        scrapeEachResultPage(EventsDatabase,driver)
        time.sleep(rand(3,9))
        LastPageTest = EvaluateIfWeAreInLastPage(driver)
        if LastPageTest==True:
            break
        else:
            pass
        action = EventSearchPagination(driver)
        if action==False:
            break
        else:
            pass
    driver.quit()
    ParentFolder = 'Event Database'
    characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for i in characters:
        Each_Keyword = Each_Keyword.replace(i,'_')
    SubFolder = Each_Keyword
    try:
        os.mkdir(os.path.join(ParentFolder,SubFolder))
    except:
        pass

    FileName = (f'{Each_Keyword} Export at {time.ctime()}.csv').replace(':','_')


    CSV_ExportFileName = os.path.join(ParentFolder,SubFolder,FileName)


    with open(CSV_ExportFileName, 'w', encoding="utf8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = EventsDatabase[0].keys())
        writer.writeheader()
        writer.writerows(EventsDatabase)
        csvfile.close()
    print(f'New File: {FileName} created')

def main():
    UserInput =  GetUserInputViaPrompt('Enter Search Keyword','Multiple Keywords must be separated by ";"')
    EvalInput = re.search(r';|; ',UserInput)
    if EvalInput==None:
        SearchEventForEachKeyword(UserInput)
    else:
        Keywords = UserInput.split(';')
        for Each_Keyword in Keywords:
            SearchEventForEachKeyword(Each_Keyword)
main()