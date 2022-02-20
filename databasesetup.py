import sqlite3
from datetime import datetime, timedelta

MINIMUM_POINT_VALUE = 3



def GetWeeklyPointValue() -> list:
    d = datetime(datetime.today().year, datetime.today().month, day=7)
    offset = -d.weekday()
    StartOfMonth = d+timedelta(offset)
    db = sqlite3.connect('donations.db')
    c = db.cursor()
    c.execute("SELECT \"character name\" FROM Characters")
    namesList = c.fetchall()
    sheetsDict = {}
    for name in namesList:
        sheetsDict[name[0]] = [0,0,0,0]


    for i in range(4):
        c.execute("SELECT * FROM Donations WHERE date BETWEEN '{}' AND '{}' ORDER BY character ASC".format(StartOfMonth+timedelta(days=(i*7)), StartOfMonth+timedelta(days=(i*7)+6)))
        newList = c.fetchall()

        for dono in newList:
            sheetsDict[dono[2]][i] += 1
    sheetsList = []
    for key in sheetsDict.keys():
        newEntry = [key]
        newEntry.extend(sheetsDict[key])
        sheetsList.append(newEntry)

    return sheetsList
    


def GetWeekDbList() -> list:
    db = sqlite3.connect('donations.db')
    c = db.cursor()
    today = datetime.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    StartOfWeek = today - timedelta(days=today.weekday())
    EndOfWeek = StartOfWeek + timedelta(days=6)

    #getting this weeks's donations
    c.execute("SELECT * FROM Donations WHERE date BETWEEN '{}' AND '{}' ORDER BY character ASC".format(StartOfWeek, EndOfWeek))
    newList = c.fetchall()
    c.execute("SELECT \"character name\" FROM Characters")
    namesList = c.fetchall()
        

    sheetsDict = {}
    for name in namesList:
        sheetsDict[name[0]] = [0,0,0,0,0,0,0,]
    for dono in newList:
        dayNumber = datetime(year=int(dono[1][0:4]), month=int(dono[1][5:7]), day=int(dono[1][8:10])).weekday()
        sheetsDict[dono[2]][dayNumber] += 1

    sheetsList = []
    for key in sheetsDict.keys():
        newEntry = [key]
        newEntry.extend(sheetsDict[key])
        sheetsList.append(newEntry)

    for i, user in enumerate(sheetsList):
        if(sum(user[1:]) >= MINIMUM_POINT_VALUE):
            sheetsList[i].append(True)
        else:
            sheetsList[i].append(False)

    return sheetsList


if __name__ == '__main__':
    GetWeeklyPointValue()