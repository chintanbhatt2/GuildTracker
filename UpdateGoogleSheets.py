from __future__ import print_function

import os.path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2 import service_account
from pyparsing import col
from rsa import compute_hash

from databasesetup import *

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


today = datetime.today()
StartOfWeek = today - timedelta(days=today.weekday())
EndOfWeek = StartOfWeek + timedelta(days=6)
sowString = StartOfWeek.strftime("%m/%d/%y")
eowString = EndOfWeek.strftime("%m/%d/%y")

SPREADSHEET_ID = '1ZdJduq8OGK0FY16Zqw4T56E7DqDnlroiL1kq8F2Ca3E'

def UpdateSheet():
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        # result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
        #                             range="Daily!B2:J28").execute()
        # values = result.get('values', [])


        # if not values:
        #     print('No data found.')
        #     return

        #get data from database
        
        sheetList = [sowString + "-" + eowString,"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","Met Quota?",]
        returnedList: list = GetWeekDbList()
        returnedList.insert(0, sheetList)

        #write changes
        print("Write changes to Daily Board? [y/n]")
        cin = input()
        if(cin == 'y'):
            request = sheet.values().update(spreadsheetId=SPREADSHEET_ID, 
            range="Daily!B2", 
            valueInputOption="RAW", 
            body={"values":returnedList}).execute() 
        else:
            pass
        print("Write changes to Weekly Board? [y/n]")
        cin = input()
        if(cin == 'y'):
            d = datetime(datetime.today().year, datetime.today().month, day=7)
            offset = -d.weekday()
            StartOfMonth = d+timedelta(offset)
            #get list of first mondays
            weeklyPointList = GetWeeklyPointValue()
            weeklyPointList.insert(0, ['',  (StartOfMonth+timedelta(days=(0*7))).date().strftime("%m/%d/%Y"), 
                                                            (StartOfMonth+timedelta(days=(1*7))).date().strftime("%m/%d/%Y"), 
                                                            (StartOfMonth+timedelta(days=(2*7))).date().strftime("%m/%d/%Y"), 
                                                            (StartOfMonth+timedelta(days=(3*7))).date().strftime("%m/%d/%Y") ])
            


            request = sheet.values().update(spreadsheetId=SPREADSHEET_ID, 
            range="Weekly!B2", 
            valueInputOption="RAW", 
            body={"values":weeklyPointList}).execute() 
        else:
            pass        


    except HttpError as err:
        print(err)

if __name__ == '__main__':
    UpdateSheet()