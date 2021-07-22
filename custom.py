import json
import time
from operator import itemgetter
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import *
from tkinter import simpledialog

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