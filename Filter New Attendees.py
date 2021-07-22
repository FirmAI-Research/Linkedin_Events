import pandas as pd
import os
import re
import csv
from custom import GetTargetFile

def LoadCSV(FileName):
    CSV_File_Name = FileName
    with open(CSV_File_Name, 'r', encoding="utf8") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=",")
        inputDict = []
        for row in reader:
            inputDict.append(row)
    return inputDict

def checkIfAttendeeAlreadyExists(LinekdInProfileID, dictionaryToCompare):
    for i in range(len(dictionaryToCompare)):
        
        if dictionaryToCompare[i]['Profile URL']==LinekdInProfileID:
            return 'Already In Our Database', dictionaryToCompare[i]
        else:
            pass
    return 'New Attendee',''

def FileterNewAttendees():
    OldScrap = LoadCSV(GetTargetFile('Select Old CSV file'))
    NewScrap = LoadCSV(GetTargetFile('Select New CSV file'))
    
    OldAttendees = []
    NewAttendees = []
    for eachDict in NewScrap:
        evaluate = checkIfAttendeeAlreadyExists(eachDict['Profile URL'],OldScrap)
        if evaluate[0]=='New Attendee':
            NewAttendees.append(eachDict)
        elif evaluate[0]=='Already In Our Database':
            OldAttendees.append(eachDict)
    return NewAttendees, OldAttendees

analysis = FileterNewAttendees()
pd.DataFrame(analysis[0],index=None).to_csv('New Attendees.csv')