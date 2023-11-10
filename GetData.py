import time
import traceback
import pandas as pd
import pymssql
import time
from log import logger as logs

def GetStrategyDetails(leg, logs):
    Data = pd.DataFrame()
    conn = False
    maxCount = 0
    while not conn:

        try:
            conn = pymssql.connect(
                server='172.20.11.62', user='sa', password='sa@123', database='JainamStrategy')
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """
            SELECT * FROM [JainamStrategy].[dbo].[TBOT_KAUS29] WITH (NOLOCK)
            WHERE Legs = {leg}
            """.format(leg=leg)
    try:

        if conn:
            Data = pd.read_sql(query, conn)
            Data = Data.iloc[0]
        else:
            logs.info('Unable to connect Strike, %s' + _message)

    except:
        logs.error("Problem in Get Strategy Details Query")
    finally:
        if conn:
            conn.close()
    return Data


def IndexPrice(Symbol, logs):
    # #this function gives you spot price you should calculate strike price accordingly.
    LivePrice = None
    conn = False
    maxCount = 0

    Symbol = 'Nifty Bank' if Symbol == 'BANKNIFTY' else None

    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.50', user='sa', password='sa@123', database='JainamFeeds')
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """
            SELECT IndexValue/100. as LivePrice
            FROM dbo.Feeds_CM_7207_Copy WITH (NOLOCK) WHERE IndexName like '{sym}'
            """.format(sym=Symbol)

    try:
        if conn:
            df = pd.read_sql(query, conn)
            if not df.empty:
                LivePrice = df['LivePrice'][0]
            else:
                logs.info("Unable to Get Live Strike Price for %s", Symbol)
        else:
            logs.error('Unable to connect JainamFeeds, %s' + _message)
    except:
        logs.error('Problem in Closest Premium Query')

    finally:
        if conn:
            conn.close()

    return LivePrice


def GetStrikePrice(price):
    strike_price = int(100 * round(price/100))
    return strike_price


def GetCurrentMarketPriceFNO(Symbol, StrikePrice, ExpiryDate, StrikeType, logs):
    LastTradingPrice = None
    Token = None
    conn = False
    maxCount = 0

    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.50', user='sa', password='sa@123', database='JainamFeeds')
        except:
            time.sleep(1)
            maxCount += 1
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """
            SELECT f.LastTradePrice/100. AS LTP,
                   f.Token AS Token
            FROM [JainamFeeds].[dbo].[Feeds_FO_7208_Copy] f WITH (NOLOCK)
            INNER JOIN [dbo].[TokenDetails] t ON f.Token = t.FOToken
            WHERE t.Symbol = '{Symbol}' 
            AND t.StrikePrice = {StrikePrice} 
            AND t.StrikeType = '{StrikeType}' 
            AND t.ExpiryDate = '{ExpiryDate}'
            """.format(Symbol=Symbol,
                       StrikePrice=StrikePrice,
                       StrikeType=StrikeType,
                       ExpiryDate=ExpiryDate)

    try:
        if conn:
            data = pd.read_sql(query, conn)
            if not data.empty:
                LastTradingPrice = data.iloc[0].LTP
                Token = str(int(data.iloc[0].Token))
            else:
                logs.info("Unable to Get Live Price For %s %s %s %s ",
                          Symbol, ExpiryDate, StrikePrice,  StrikeType)
        else:
            logs.error('Unable to connect JainamFeeds, %s' + _message)

    except:
        logs.error('Problem in Get Current Market Price FNO Query')

    finally:
        if conn:
            conn.close()

    return LastTradingPrice, Token


def GetClosestPremium(Symbol, ExpiryDate, StrikeType, Premium, logs):
    Token = None
    LastTradingPrice = None
    StrikePrice = None
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.50', user='sa', password='sa@123', database='JainamFeeds')
        except:
            time.sleep(1)
            maxCount += 1
            print(f"Tring to connect JainamFeeds attempt {maxCount}")
            logs.error(traceback.format_exc())
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """
            SELECT TOP(1)
                f.Token,
                t.SymbolWithExpiry,
                t.Symbol,
                t.ExpiryDate,
                t.StrikePrice,
                t.StrikeType,
                f.LastTradePrice/100. AS LTP,
                ABS(f.LastTradePrice/100. - {premium}) AS diff,
                f.InsDt

            FROM dbo.Feeds_FO_7208_Copy f WITH(NOLOCK)
            INNER JOIN (SELECT * FROM [172.20.11.101].[TokenDB].[dbo].[TokenDetails]
                WHERE Symbol = '{symbol}'
                AND ExpiryDate = '{expirydate}'
                AND StrikeType = '{striketype}' )t ON t.FOToken = f.Token

            ORDER BY ABS(f.LastTradePrice/100. - {premium}) ASC
            """.format(symbol=Symbol, expirydate=ExpiryDate, striketype=StrikeType, premium=Premium)
    try:
        if conn:
            Data = pd.read_sql(query, conn)
            if not Data.empty:
                Token = Data['Token'].iloc[0]
                LastTradingPrice = Data['LTP'].iloc[0]
                StrikePrice = Data['StrikePrice'].iloc[0]
            else:
                logs.warnings(
                    f"Unable to Get Closest Premium {Premium} for {Symbol} {ExpiryDate} {StrikeType}")
        else:
            logs.warnings('Unable to connect JainamFeeds, %s' + _message)
    except:
        logs.warnings('Problem in Closest Premium Query')
        logs.error(traceback.format_exc())

    finally:
        if conn:
            conn.close()
    return Token, StrikePrice, LastTradingPrice


def GetFNOSymbolToken(Symbol, StrikePrice, ExpiryDate, StrikeType):
    Token = None
    conn = False
    maxCount = 0
    while not conn:
        try:
            conn = pymssql.connect(
                server='172.20.11.101', user='sa', password='sa@123', database='TokenDB')
        except:
            time.sleep(1)
            maxCount += 1
            print(f"Tring to connect JainamFeeds attempt {maxCount}")
            logs.error(traceback.format_exc())
            if maxCount == 3:
                _message = "max tries exceeded"
                break

    query = """
            SELECT FOToken FROM [TokenDB].[dbo].[TokenDetails]
            WHERE Symbol = '{Symbol}'
            AND ExpiryDate = '{ExpiryDate}'
            AND StrikeType = '{StrikeType}'
            AND StrikePrice = {StrikePrice}
            """.format(Symbol=Symbol, StrikePrice=StrikePrice, ExpiryDate=ExpiryDate, StrikeType=StrikeType)
    try:
        if conn:
            Data = pd.read_sql(query, conn)
            if not Data.empty:
                Token = Data['FOToken'].iloc[0]
            else:
                logs.info(
                    f"Unable to Get Token for {Symbol} {ExpiryDate} {StrikePrice} {StrikeType}")
        else:
            logs.error('Unable to connect TokenDB, %s' + _message)
    except:
        logs.error('Problem in Get Token Query')
        logs.error(traceback.format_exc())

    finally:
        if conn:
            conn.close()
    return Token