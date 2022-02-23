from datetime import date, datetime
from time import sleep
from rich.console import Console, Group
from rich.prompt import Confirm
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from PIL import ImageGrab
import cv2 
import pytesseract
import re
import json
import sqlite3

from uritemplate import expand

from UpdateGoogleSheets import UpdateSheet

IMG_DEBUG = False
CONSOLE_OUTPUT = False
EXCEL_OUTPUT = True
JSON_ENABLED = False

console = Console()

def GrabFromClipboard():
    im = ImageGrab.grabclipboard()
    im.save("images/clipboard/clipImage.png", "PNG")

def ConsoleFlush():
    console.clear()
    console.rule("[bold cyan]✧･ﾟ: *✧･ﾟ:*[/bold cyan] [magenta] Gremlin Guild Tracker [magenta/][bold cyan]*:･ﾟ✧*:･ﾟ✧.", style="magenta")

def main():
    db = sqlite3.connect('donations.db')
    c = db.cursor()

    ConsoleFlush()


    if(IMG_DEBUG==False):
        console.line(count=2)


        console.print("Have you taken a screenshot of your whole screen? If not, please do so now and then press enter to continue.", style="red", justify="center")
        console.input()
        console.clear()
        console.rule("[bold cyan]✧･ﾟ: *✧･ﾟ:*[/bold cyan] [magenta] Gremlin Guild Tracker [magenta/][bold cyan]*:･ﾟ✧*:･ﾟ✧.", style="magenta")
        while(True):
            try:
                GrabFromClipboard()
                break;
            except:
                ConsoleFlush()
                console.print("You silly goose, you didn't copy the image! Press enter when you're ready to try again", style="bold red", justify="center")
                console.input()

        ConsoleFlush()
        fullString = ''
        console.print("Image Sucessfully copied! Loading image now.", style="bold green", justify="center")
        with console.status("Loading image", spinner="hearts", speed=0.25):
            img = cv2.imread('images/clipboard/clipImage.png')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ConsoleFlush()
        console.print("Image Sucessfully loaded! Scanning for text now.", style="bold green", justify="center")
        with console.status("Reading image", spinner="hearts", speed=0.25):
            fullString = pytesseract.image_to_string(img)



        fullString = fullString.split('\n')

        reggie = re.compile(r'^\[')
        filteredString = [i for i in fullString if reggie.match(i)]

        if(len(filteredString) < 5 ):
            ConsoleFlush()
            console.print("ERROR: Could not recognize image. Are you sure you copied the right thing?", style="bold underline red")
            sleep(2)
            console.print("Exiting script now")
            quit()


    if(IMG_DEBUG==False and JSON_ENABLED == True):
        importedJson:dict = json.load(open('donations.json', 'r'))
        for firstPerson in filteredString:
            DonoString = re.findall(r'\[(.*?)\]', firstPerson)
            if(DonoString[1] != "Donation"):
                pass
            else:
                transactionDate = re.search(r"\d*/\d*/\d*", firstPerson).group(0)
                transactionAmount = re.search(r"Guild Bloodstone x\d*", firstPerson).group(0)
                transactionUser = re.search(r"through \w*", firstPerson).group(0)
                transactionTotal = re.search(r'currently has \d{1,3}(,\d{3})*(\.\d+)?', firstPerson).group(0)
                transactionKind = re.search(r'Donate \w*', firstPerson).group(0)

                Date = datetime.strptime(transactionDate, '%m/%d/%Y')
                DateStr = Date.isoformat()
                Amount = int(transactionAmount[18:])
                User = transactionUser[8:]
                Total = int(transactionTotal[14:].replace(',',''))
                Type = transactionKind[7:]

                #adding new entries
                if(User not in importedJson):
                    nJSONObject = {
                        'real_name':'INSERT_NAME',
                        'last_paid':DateStr,
                        'dates_paid':{
                            DateStr : {
                                'type':{
                                    'Silver':True if(Type=="Silver") else False,
                                    'Gold':True if(Type=="Gold") else False,
                                    'Donation Banner':True if(Type=="Donation Banner") else False
                                    },
                                'amount': Amount,
                                }
                            }
                        }
                    importedJson[User] = nJSONObject
                else:
                    if(DateStr not in importedJson[User]['dates_paid']):
                        importedJson[User]['dates_paid'][DateStr] = {                    
                            'type':{
                                    'Silver':True if(Type=="Silver") else False,
                                    'Gold':True if(Type=="Gold") else False,
                                    'Donation Banner':True if(Type=="Donation Banner") else False
                                    },
                                'amount': Amount,}
                    else:
                        if(importedJson[User]['dates_paid'][DateStr]['type'][Type]==False):
                            importedJson[User]['dates_paid'][DateStr]['type'][Type] = True
                            importedJson[User]['dates_paid'][DateStr]['amount'] = importedJson[User]['dates_paid'][DateStr]['amount'] + Amount
                if(datetime.fromisoformat(importedJson[User]['last_paid']) < Date):
                    importedJson[User]['last_paid']=DateStr
        json.dump(importedJson, open("donations.json", "w"), sort_keys=True, default=str, indent=4)

    else:
        for firstPerson in filteredString:
            DonoString = re.findall(r'\[(.*?)\]', firstPerson)
            if(DonoString[1] != "Donation"):
                pass
            else:
                transactionDate = re.search(r"\d*/\d*/\d*", firstPerson).group(0)
                transactionAmount = re.search(r"Guild Bloodstone x\d*", firstPerson).group(0)
                transactionUser = re.search(r"through \w*", firstPerson).group(0)
                transactionTotal = re.search(r'currently has \d{1,3}(,\d{3})*(\.\d+)?', firstPerson).group(0)
                transactionKind = re.search(r"('s|’s) \w* \w*", firstPerson).group(0)

                Date = datetime.strptime(transactionDate, '%m/%d/%Y')
                DateStr = Date.isoformat()
                Amount = int(transactionAmount[18:])
                User = transactionUser[8:]
                Total = int(transactionTotal[14:].replace(',',''))
                Type = transactionKind[3:]
                if(Type[0:5] == "Honor"):
                    Type = "Honor"
                else:
                    Type = Type[7:]

                #adding new entries
                try:
                    c.execute("INSERT INTO Characters VALUES ('{}', '{}', {}, '{}')".format(User, 'Valtan', '0', "_"))
                except:
                    pass
                c.execute("SELECT * FROM donations WHERE date='{}' AND type='{}' AND Character='{}'".format(Date, Type, User))
                returnList = c.fetchall()
                if(len(returnList) == 0):
                    c.execute("INSERT INTO Donations (Date, Character, Type, Amount) VALUES ('{}' , '{}', '{}', {})".format(Date, User, Type, Amount))
                    


        db.commit()
    ConsoleFlush()
    console.print("""
     ******       ******
   **********   **********
 ************* *************
*****************************
*****************************
*****************************
 ***************************
   ***********************
     *******************
       ***************
         ***********
           *******
             ***
    """, style="magenta", justify='full')
    console.print("Script is done parsing!", justify='center')
    continueOrNot = Confirm.ask("Would you like to update the sheet?")
    if(not continueOrNot):
        console.print("Exiting application...")
        quit()

    UpdateSheet()



    # ConsoleFlush()
    # if(CONSOLE_OUTPUT==True):
    #     table = Table(title='Highest Contributers', style="bold green")
    #     table.add_column('user', justify='left', no_wrap='true')
    #     table.add_column('contributions', justify='right', no_wrap='true')
    #     table.add_row('testing1', '50')
    #     table.add_row('testing3', '30')
    #     table.add_row('testinasdfg1', '20')



    #     layout = Layout()
    #     layout.split_row(
    #         Layout(name='Left'),
    #         Layout(name='Right'),
    #     )
    #     layout['Left'].split_column(
    #         Layout(name='Ranking'),
    #         Panel("", title="Not Met Quota"),
    #     )
    #     # layout['Left']['Ranking'].split_row(
    #     #     Panel("1.{}\n2.{}".format(HighestContributer[0], HighestContributer[1]), title="Highest Contibuters", border_style="green", style="green"),
    #     #     Panel("Hello, [red]World!", title="Lowest Contibuters", border_style="bold red", highlight=True), 

    #     # )
    #     layout['Left']['Ranking'].split_row(
    #         table,
    #         Panel("Hello, [red]World!", title="Lowest Contibuters", border_style="bold red", highlight=True), 

    #     ) 

    #     console.print(layout)


if __name__ == "__main__":
    main()
