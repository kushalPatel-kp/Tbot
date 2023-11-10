import time
import traceback
import pandas as pd
import pymssql


def IsHoliday():
    holiday = True
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.101', user='jnm', password='Jscpl@123', database='JainamSpace')
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = '''
            DECLARE @Today AS VARCHAR(100)
            SET @Today = CONVERT(DATE, GETDATE())

            IF EXISTS (SELECT HolidayDate FROM JainamSpace.dbo.Holiday_master
                                WHERE HolidayDate =  @Today
                                AND TradingHolidayEQFNO = 'Close' )
            BEGIN
            SELECT IsHoliday = 1
            END
            ELSE
            BEGIN
                SELECT IsHoliday = 0
            END
            '''
    try:
        if conn:
            Data = pd.read_sql(query, conn)
            if not Data.empty:
                holiday = Data.values[0][0]
            else:
                print("Problem in Holiday Query...")
        else:
            print("Holiday Server not connected...")
    except:
        print(traceback.format_exc())
    finally:
        if conn:
            conn.close()

    return holiday


def CheckIsHoliday(Date):
    # Date Format : YYYY-MM-DD
    holiday = True
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.101', user='jnm', password='Jscpl@123', database='JainamSpace')
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = '''
            DECLARE @Today AS VARCHAR(100)
            --SET @Today = CONVERT(DATE, '{Date}')
            SET @Today = '{Date}'

            IF EXISTS (SELECT HolidayDate FROM JainamSpace.dbo.Holiday_master
                                WHERE HolidayDate =  @Today
                                AND TradingHolidayEQFNO = 'Close' )
            BEGIN
            SELECT IsHoliday = 1
            END
            ELSE
            BEGIN
                SELECT IsHoliday = 0
            END
            '''.format(Date=Date)
    try:
        if conn:
            Data = pd.read_sql(query, conn)
            if not Data.empty:
                holiday = Data.values[0][0]
            else:
                print("Problem in Holiday Query...")
        else:
            print("Holiday Server not connected...")
    except:
        print(traceback.format_exc())
    finally:
        if conn:
            conn.close()

    return holiday
