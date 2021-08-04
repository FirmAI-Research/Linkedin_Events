import json
import time
from operator import itemgetter
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import *
from tkinter import simpledialog
import re
from datetime import datetime
from datetime import date

def prepareCookies(driver):
    json_cookie = 'LinkedIn Cookies/cookiebro-domaincookies-.www.linkedin.com.json'
    driver.delete_all_cookies()
    driver.get("https://www.linkedin.com/")
    with open(json_cookie, 'r', encoding="utf8") as json_s:
        star_data = json.load(json_s)
        for i in star_data:
            try:
                driver.add_cookie({'name':i['name'],'value':i['value']})
            except:
                input('cookie add failed for:\n'+ i)
    time.sleep(4)
    while True:
        try:
            driver.get('https://www.linkedin.com/')
            break
        except:
            pass


def EvaluateIfWeAreInLastPage(driver):
    try:
        Test = driver.find_element_by_xpath('//button[@disabled]')
        return True
    except:
        return False

def GetTargetDirectory(title):
    root = Tk()
    root.withdraw()
    folder_selected = askdirectory(title=title)
    return folder_selected

def GetTargetFile(title):
    root = Tk()
    root.withdraw()
    filename = askopenfilename(title=title)
    return filename

def GetUserInputViaPrompt(title,prompt):
    ROOT = Tk()
    ROOT.geometry("400x200")
    ROOT.withdraw()
    USER_INP = simpledialog.askstring(title=title,prompt=prompt)
    return USER_INP


def SortListByDicionaryKeyValue(list_to_sort , key_name):
    newlist = sorted(list_to_sort, key=itemgetter(key_name))
    return newlist


def CallDateTime(OriginalDateString):
    T = re.search('- .+2021',OriginalDateString)
    if T!=None:
        Type = 'Starts with Month'
        Dates = OriginalDateString.split(' - ')
        Date_1, Date_2 = re.sub(', \d{1,2}:.+$','',Dates[0]), re.sub(', \d{1,2}:.+$','',Dates[1])
        #return Type, Date_1, Date_2
    else:
        Type = 'Starts with WeekDay'
        Date_1 = re.sub(', \d{1,2}:.+$','',OriginalDateString)
        Date_2 = None
        #return Type, Date_1, Date_2
    
    if Type=='Starts with Month':
        First_Date = datetime.strptime(Date_1,"%b %d, %Y").date()
        Second_Date = datetime.strptime(Date_2,"%b %d, %Y").date()
    elif Type=='Starts with WeekDay':
        First_Date = datetime.strptime(Date_1,"%a, %b %d, %Y").date()
        Second_Date = None
    
    Day_to_Go_From_First_Date = (First_Date - date.today()).days
    if Second_Date==None:
        Day_to_Go_From_Second_Date = ''
    else:
        Day_to_Go_From_Second_Date = (Second_Date - date.today()).days
    
    return First_Date,Second_Date,Day_to_Go_From_First_Date,Day_to_Go_From_Second_Date
