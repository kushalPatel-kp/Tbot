import warnings
from datetime import datetime
import traceback
from GetData import GetStrategyDetails
from GetExpiryDate import GetCurreentExpirydate
from UpdateTradeDetails import UpdateExpiryDate

def configEntryConditions(Leg, logs):
    Leg_Data = GetStrategyDetails(Leg, logs)

    try:
        Symbol = Leg_Data['IndexName']
    except:
        logs.error(traceback.format_exc())
        Symbol = None

    try:
        ExpiryDate = GetCurreentExpirydate(Symbol)
        UpdateExpiryDate(ExpiryDate,Leg, logs)
    except:
        logs.error(traceback.format_exc())
        ExpiryDate = None

    try:
        Lots = Leg_Data['Lots']
    except:
        logs.error(traceback.format_exc())
        Lots = None

    try:
        StrikeType = Leg_Data['StrikeType']
    except:
        logs.error(traceback.format_exc())
        StrikeType = None

    try:
        Action = Leg_Data['Action']
    except:
        logs.error(traceback.format_exc())
        Action = None

    try:
        StopLossValue = Leg_Data['StopLossValue']
    except:
        logs.error(traceback.format_exc())
        StopLossValue = None

    try:
        StrikeGap = float(Leg_Data['StrikeGap'])
    except:
        logs.error(traceback.format_exc())
        StrikeGap = None

    try:
        Premimum=Leg_Data['Premimum']
    except:
        logs.error(traceback.format_exc())
        Premimum=None

    try:
        if str(Leg_Data['InsDt'].date()) != str(datetime.today().date()):
            StoplossFlag = True
        else:
            StoplossFlag = Leg_Data['StoplossFlag']
    except:
        logs.error(traceback.format_exc())
        StoplossFlag=True

    # try:
    #     StoplossFlag = True if not Leg_Data['StoplossFlag'] else Leg_Data['StoplossFlag'] if str(
    #         Leg_Data['InsDt'].date()) == str(datetime.today().date()) else None
    # except:
    #     logs.error(traceback.format_exc())
    #     StoplossFlag = None
    
    try:
        StrikePrice = None if not Leg_Data['StrikePrice'] else Leg_Data['StrikePrice'] if str(
            Leg_Data['InsDt'].date()) == str(datetime.today().date()) else None
    except:
        logs.error(traceback.format_exc())
        StrikePrice = None

    try:
        StopLossOrderId = None if not Leg_Data['StoplossOderID'] else Leg_Data['StoplossOderID'] if str(
            Leg_Data['InsDt'].date()) == str(datetime.today().date()) else None
    except:
        logs.error(traceback.format_exc())
        StopLossOrderId = None

    try:
        SquareOffAction = None if not Leg_Data['StrikePrice'] else 'SELL' if Leg_Data[
            'Action'] == 'BUY' else 'BUY' if Leg_Data['Action'] == 'SELL' else None
    except:
        logs.error(traceback.format_exc())
        SquareOffAction = None

    try:
        if StrikePrice:
            # StopLossPrice = (EntryPrice + (EntryPrice * (StopLossValue/100)))
            Stoploss_Price = (Leg_Data['EntryPrice'] + (Leg_Data['EntryPrice'] * (
                Leg_Data['StopLossValue']/100))) if Leg_Data['StopLossValue'] else None
        else:
            Stoploss_Price = None
    except:
        logs.error(traceback.format_exc())
        Stoploss_Price = None

    LegDeatails = {"Leg": Leg, "Symbol": Symbol, "Action": Action,  "ExpiryDate": ExpiryDate, "StrikePrice": StrikePrice,"StrikeGap": StrikeGap, "StrikeType": StrikeType,"Premimum":Premimum,
                   "Lots": Lots, "SquareOffAction": SquareOffAction, "StopLossValue": StopLossValue, "StopLossOderId": StopLossOrderId, "StopLossPrice": Stoploss_Price, "StoplossFlag":StoplossFlag}

    return LegDeatails

# warnings.filterwarnings('ignore')
# print(configEntryConditions(1, None))
# print(configEntryConditions(2, None))
# print(configEntryConditions(3, None))
# print(configEntryConditions(4, None))
