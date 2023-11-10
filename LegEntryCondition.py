import json
import traceback
import requests
from FormatExpiryDate import ChangeExpiryDateFormat
from GetData import GetCurrentMarketPriceFNO, GetStrikePrice, IndexPrice,GetClosestPremium
from UpdateTradeDetails import UpdateEntryTradeDetails,UpdateStopLossFlag

def Leg_Entry(Leg_Data, url, logs):

    MAX_TRADE_COUNT = 0

    response = None

    # Initially by default in table the stoploss flag is True
    # stoplossflag = 1 means stoploss flag is True
    # stoplossflag = 0 means stoploss flag is False

    if Leg_Data:
        Leg = Leg_Data['Leg']
        Symbol = Leg_Data['Symbol']
        StrikeType = Leg_Data['StrikeType']
        StrikeGap = Leg_Data['StrikeGap']
        ExpiryDate = Leg_Data['ExpiryDate']
        TradeAction = Leg_Data['Action']
        StopLossValue = Leg_Data['StopLossValue']
        Premimum = Leg_Data['Premimum']
        StopLossPrice = 0.00

        IndexLivePrice = IndexPrice(Symbol, logs)

        if IndexLivePrice:
            AtTheMoneyPrice = GetStrikePrice(IndexLivePrice)

            if not Premimum:
                if StopLossValue and StopLossValue != 0:
                    if TradeAction == "SELL":
                        StrikePrice = AtTheMoneyPrice + StrikeGap
                        LastTradingPrice, Token = GetCurrentMarketPriceFNO(Symbol, StrikePrice, ExpiryDate, StrikeType, logs)
                        StopLossPrice = round(LastTradingPrice + (LastTradingPrice * (StopLossValue/100)), 2)
            else:
                Token, StrikePrice, LastTradingPrice = GetClosestPremium(Symbol, ExpiryDate, StrikeType, Premimum, logs=logs)
                
            # maxtrade count is less than 3
            if MAX_TRADE_COUNT < 3:
                headers = {
                    'Content-type': 'application/json',
                    'Accept': 'application/json'
                }

                data = {
                    "StrategyName": "T29",
                    "Type": "Entry",  # Entry/Exit
                    "Token": str(Token),
                    "Symbol": "BANKNIFTY",
                    "InstrumentName": "OPTIDX",
                    "Signal": str(TradeAction).capitalize(),  # Buy/Sell
                    "ExpiryDate": str(ExpiryDate),
                    "ExpiryDateForOdin": str(ChangeExpiryDateFormat(ExpiryDate)),
                    "StrikeType": str(StrikeType),  # CE/PE
                    "StrikePrice": str(StrikePrice),
                    "LTP": str(LastTradingPrice),
                    "Leg": str(Leg),  # 1 / 2 / 3 / 4
                    "TargetPrice": "0.00",
                    "StopLossPrice": str(StopLossPrice),
                }

                data = json.dumps(data)

                req = requests.post(url, data, headers=headers)
                response = json.loads(req.text)

                logs.info('Leg : %s, Entry Order Request Placed, For %s %s %s %s %s at %s with SL of %s', Leg,
                            TradeAction, Symbol, ExpiryDate, StrikePrice, StrikeType, LastTradingPrice, StopLossPrice)
                try:
                    if response and response['success']:
                        UpdateEntryTradeDetails(Leg, AtTheMoneyPrice, StrikePrice, LastTradingPrice, logs)

                        SquareOffAction = 'SELL' if TradeAction == 'BUY' else 'BUY' if TradeAction == 'SELL' else ''

                    else:
                        SquareOffAction = None
                except:
                    logs.info('Leg : %s, Response : %s', Leg, response)
                    logs.error(str(traceback.format_exc()))
            else:
                logs.info('Leg : %s, MAX TRADE COUNT EXCEED, For %s %s %s %s %s',Leg, TradeAction, Symbol, ExpiryDate, StrikePrice, StrikeType,)
        else:
            logs.error('Leg : %s, Unable to Get Live Price For %s %s %s %s',
                        Leg, TradeAction, Symbol, ExpiryDate, StrikeType,)
            Token, StrikePrice, LastTradingPrice, SquareOffAction, StopLossOderId, StopLossPrice = None, None, None, None, None, None
    else:
        logs.error('Leg: %s, No Live Price Symbol: %s, ExpiryDate: %s, StrikeType: %s, Premium: %s',
                    Leg, Symbol, ExpiryDate, StrikeType, StrikeGap)
        Token, StrikePrice, LastTradingPrice, SquareOffAction, StopLossOderId, StopLossPrice = None, None, None, None, None, None

    Leg_Data["Leg"] = Leg
    Leg_Data["Symbol"] = Symbol
    Leg_Data["Token"] = Token
    Leg_Data["ExpiryDate"] = ExpiryDate
    Leg_Data["StrikePrice"] = StrikePrice
    Leg_Data["StrikeType"] = StrikeType
    Leg_Data["SquareOffAction"] = SquareOffAction
    Leg_Data['StopLossPrice'] = StopLossPrice

    return Leg_Data
