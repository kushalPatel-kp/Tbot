import time
import traceback
import pymssql


def UpdateEntryTradeDetails(Leg, ATM, StrikePrice, Price,logs):
    # Leg, AtTheMoneyPrice, StrikePrice, EntryPrice, logs
    UpdateStatus = False
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.62', user='sa', password='sa@123', database='JainamStrategy')
            cursor = conn.cursor()
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """ 
            UPDATE [dbo].[TBOT_KAUS29]
            SET ATM = '{ATM}',
                EntryPrice = '{Price}',
                StrikePrice = '{StrikePrice}',
                ExitTime = NULL,
                ExitPrice = NULL,
                StopLossPrice = NULL,
                StoplossOderID = NULL,
                InsDt = GETDATE()
            WHERE Legs = {Leg}
            """.format(Leg=Leg, ATM=ATM, StrikePrice=StrikePrice, Price=Price)

    try:
        if conn:
            # print(query)
            cursor.execute(query)
            conn.commit()
            UpdateStatus = True
        else:
            print(traceback.format_exc())
            logs.error('Unable to connect Strike, ' + _message)
    except:
        print(query)
        print(traceback.format_exc())
        logs.error("Unable to update details in table for Leg %s", Leg)
    finally:
        if conn:
            conn.close()
    return UpdateStatus


def UpdateExitPrice(Leg, ExitPrice, logs):

    UpdateStatus = False
    conn = False
    maxCount = 0

    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.62', user='sa', password='sa@123', database='JainamStrategy')
            cursor = conn.cursor()
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """ UPDATE [dbo].[TBOT_KAUS29]
                SET [ExitPrice] = '{ExitPrice}',
                    [InsDt] = GETDATE()
                WHERE [Legs] = {Leg}
                """.format(Leg=Leg, ExitPrice=ExitPrice)

    try:
        if conn:
            cursor.execute(query)
            conn.commit()
            UpdateStatus = True
        else:
            logs.error('Unable to connect Strike, ' + _message)
    except:
        print(query)
        print(traceback.format_exc())
        logs.error("Unable to update details in table for Leg %s", Leg)
    finally:
        if conn:
            conn.close()
    return UpdateStatus


def UpdateExpiryDate(ExpiryDate, leg, logs):
    UpdateStatus = False
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.62', user='sa', password='sa@123', database='JainamStrategy')
            cursor = conn.cursor()
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """
            UPDATE [dbo].[TBOT_KAUS29]
            SET [ExpiryDate] = '{ExpiryDate}'
            WHERE [Legs] = {leg}
            """.format(leg=leg, ExpiryDate=str(ExpiryDate))
    try:
        if conn:
            cursor.execute(query)
            conn.commit()
            UpdateStatus = True
        else:

            logs.error('Unable to connect Strike, ' + _message)
    except:
        print(query)
        print(traceback.format_exc())
        logs.error("Unable to update Expirydate in table for %s", leg)
    finally:
        if conn:
            conn.close()
    return UpdateStatus


def UpdateStopLossPrice(Leg,Price, logs):
    UpdateStatus = False
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.62', user='sa', password='sa@123', database='JainamStrategy')
            cursor = conn.cursor()
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """ UPDATE [dbo].[TBOT_KAUS29]
                SET [StopLossPrice] = {Price}
                WHERE [Legs] = {Leg}
                """.format(Leg=Leg, Price=Price)

    try:
        if conn:
            cursor.execute(query)
            conn.commit()
            UpdateStatus = True
        else:
            logs.error('Unable to connect Strike, ' + _message)
    except:
        print(query)
        print(traceback.format_exc())
        logs.error("Unable to update details in table for Leg %s", Leg)
    finally:
        if conn:
            conn.close()
    return UpdateStatus


def UpdateStopLossFlag(Leg,logs):
    UpdateStatus = False
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.62', user='sa', password='sa@123', database='JainamStrategy')
            cursor = conn.cursor()
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """ UPDATE [dbo].[TBOT_KAUS29]
                SET [StoplossFlag] = 1
                WHERE [Legs] = {Leg}
                """.format(Leg=Leg)

    try:
        if conn:
            cursor.execute(query)
            conn.commit()
            UpdateStatus = True
        else:
            logs.error('Unable to connect Strike, ' + _message)
    except:
        print(query)
        print(traceback.format_exc())
        logs.error("Unable to update details in table for Leg %s", Leg)
    finally:
        if conn:
            conn.close()
    return UpdateStatus


def UpdateStopLosshitFlag(Leg,logs):
    UpdateStatus = False
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.62', user='sa', password='sa@123', database='JainamStrategy')
            cursor = conn.cursor()
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """ UPDATE [dbo].[TBOT_KAUS29]
                SET [StoplossFlag] = 0
                WHERE [Legs] = {Leg}
                """.format(Leg=Leg)

    try:
        if conn:
            cursor.execute(query)
            conn.commit()
            UpdateStatus = True
        else:
            logs.error('Unable to connect Strike, ' + _message)
    except:
        print(query)
        print(traceback.format_exc())
        logs.error("Unable to update details in table for Leg %s", Leg)
    finally:
        if conn:
            conn.close()
    return UpdateStatus
