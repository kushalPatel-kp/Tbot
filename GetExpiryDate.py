import datetime
import time
import traceback
from Holidays import CheckIsHoliday
import pandas as pd
import numpy as np
import pymssql
from log import logger as logs


def GetWeeklyExpiryDate():
    today = datetime.date.today()
    ExpiryDate = today + datetime.timedelta((3-today.weekday()) % 7)
    while CheckIsHoliday(ExpiryDate):
        ExpiryDate = ExpiryDate - datetime.timedelta(days=1)

    if ExpiryDate < today:
        ExpiryDate = ExpiryDate + datetime.timedelta(days=7)
    while CheckIsHoliday(ExpiryDate):
        ExpiryDate = ExpiryDate - datetime.timedelta(days=1)

    return ExpiryDate

def GetCurreentExpirydate(Symbol):
    ExpiryDate = None
    conn = False
    maxCount = 0
    _message = ""
    while not conn:
        try:
            conn = pymssql.connect(  # type: ignore
                server='172.20.11.101', user='jnm', password='Jscpl@123', database='TokenDB')
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

        Weekly = """
            --weekly Expiry
            SELECT DISTINCT ExpiryDate
            FROM dbo.TokenDetails WITH(NOLOCK)
            WHERE Symbol = '{Symbol}'
            AND OptionType = 'OPTIDX'
            ORDER BY ExpiryDate
            """.format(Symbol=Symbol)

        try:
            if conn:

                df = pd.read_sql(Weekly, conn)
                
                Today = datetime.date.today()
            
                if not df.empty:
                    N=0
                    ExpiryDate = df.ExpiryDate.iloc[N]   
                    # print((ExpiryDate))           
                    while ExpiryDate < Today:
                        N = N +1
                        ExpiryDate = df.ExpiryDate.iloc[N]
                    
                else:
                    logs.info("Unable to Get Expiry for %s", Symbol)
            else:
                logs.error('Unable to connect 101 Token DB, %s' + _message)
        except:
            print(traceback.format_exc())
            logs.error('Problem in Get Expiry Deatils Query')

        finally:
            if conn:
                conn.close()

        return ExpiryDate