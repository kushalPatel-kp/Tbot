from datetime import datetime, timedelta
import multiprocessing
import time
import warnings
from LegEntryCondition import Leg_Entry
from LegStoplossCondition import checkstoploss
from LegExitCondtion import Leg_Exit
from EntryConditions import configEntryConditions
from Holidays import IsHoliday
from log import CleanLogFiles, logger as logs
warnings.filterwarnings("ignore")

# EntryTime = (datetime.now() + timedelta(seconds=10)).strftime('%H:%M')
# ExitTime =(datetime.now() + timedelta(minutes=3)).strftime('%H:%M')

def main(leg):
    
    EntryTime = '09:25'
    ExitTime = '15:15'

    EntryFlag = True
    ExitFlag = True

    printEntry = True
    printExit = True

    StoplossFlag = True

    # url for live
    url = "https://strike.jainam.in/api/ClientDashboard/InsertSignalOfStrategy"

    LegEntry = configEntryConditions(leg, logs)

    while True:

        if datetime.now().strftime("%H:%M") >= '09:00' and datetime.now().strftime("%H:%M") <= ExitTime:
            if datetime.now().strftime("%H:%M") < EntryTime and EntryFlag and printEntry:
                print(f"Leg : {leg} First Entry will be on {EntryTime} AM", end="\n") 
                printEntry = False

            if datetime.now().strftime("%H:%M") == EntryTime and EntryFlag:
                EntryFlag = False
                LegEntry = Leg_Entry(LegEntry, url, logs)

            if datetime.now().strftime("%H:%M") > EntryTime and datetime.now().strftime("%H:%M") < ExitTime and StoplossFlag:
                EntryFlag = False

            if StoplossFlag and not EntryFlag:
                LegEntry = checkstoploss(LegEntry, EntryTime, ExitTime, url, logs)
                StoplossFlag = False

            if datetime.now().strftime("%H:%M") > EntryTime and datetime.now().strftime("%H:%M") < ExitTime and ExitFlag and printExit:
                printExit = False
                print(f"Leg : {leg} Exit will be on {ExitTime} PM", end="\n")

            if datetime.now().strftime("%H:%M") == ExitTime and ExitFlag:
                ExitFlag = False
                Leg_Exit(LegEntry,url,logs)

            if datetime.now().strftime("%H:%M") < EntryTime:
                print(f"{datetime.now().strftime('%A %d %b %Y %H:%M:%S')}{' '*35}", end="\r")
            
            time.sleep(1)
        else:
            break

if __name__ == '__main__':
    multiprocessing.freeze_support()
    ExecutionDay = ['Tuesday', 'Wednesday', 'Thursday' ,'Friday']
    DayChanged = True
    logs.info(f'TBOT 29 EXE Start......')

    while True:
        if DayChanged:
            print("This Strategy TBOT KAUS 29 Runs on ",ExecutionDay)
            Today = str(datetime.today().strftime('%A'))

        if Today in ExecutionDay and datetime.now().strftime("%H:%M") >= "09:00" and datetime.now().strftime("%H:%M") <= '15:15' and not IsHoliday():

            L1 = multiprocessing.Process(target=main, args=(1,))
            L2 = multiprocessing.Process(target=main, args=(2,))
            L3 = multiprocessing.Process(target=main, args=(3,))
            L4 = multiprocessing.Process(target=main, args=(4,))

            Leg_Process = [L1, L2, L3, L4]
            logs.info(f'Multiprocessing start .... {Leg_Process}')

            for Leg in Leg_Process:
                Leg.start()

            for Leg in Leg_Process:
                Leg.join()

            time.sleep(60)

        else:
            if str(datetime.today().strftime('%A')) != Today:
                Today = str(datetime.today().strftime('%A'))
                DayChanged = True
                print(f"Date Changed {datetime.today().strftime('%A')}", end="\n")
                CleanLogFiles()

            else:
                DayChanged = False

            print(datetime.now().strftime('%A %d %b %Y %H:%M:%S'), end="\r")
            time.sleep(1)
