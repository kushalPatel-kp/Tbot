import traceback
import requests
import json
from GetData import GetCurrentMarketPriceFNO
from FormatExpiryDate import ChangeExpiryDateFormat
from UpdateTradeDetails import UpdateExitPrice,UpdateStopLossFlag

def Leg_Exit(leg_details,url, logs):

    MAX_TRADE_COUNT = 0
    response = None
    
    # Stoplossflag = 1 means stoploss flag is True
    # Stoplossflag = 0 means stoploss flag is False

    if leg_details :

        Leg = leg_details['Leg']
        Symbol = leg_details['Symbol']
        ExpiryDate = leg_details['ExpiryDate']
        StrikePrice = leg_details['StrikePrice']
        StrikeType = leg_details['StrikeType']
        SquareOffAction = leg_details['SquareOffAction']
        StoplossFlag = leg_details['StoplossFlag']

        # If Stoploss not hit or Stoploss order Not Executed
        if SquareOffAction and StoplossFlag:

            # Get Current Market Price
            LastTradingPrice, Token = GetCurrentMarketPriceFNO(Symbol, StrikePrice, ExpiryDate, StrikeType, logs)

            # If Current Market PRice is available
            if LastTradingPrice:

                # maxtrade count is less than 3, in best case it should take only one entry but in worst case it should not take more than 3 trades
                if MAX_TRADE_COUNT < 3:
                    headers = {
                        'Content-type': 'application/json',
                        'Accept': 'application/json'
                    }

                    data = {
                        "StrategyName": "T29",
                        "Type": "Exit",  # Entry/Exit
                        "Token": str(Token),
                        "Symbol": "BANKNIFTY",
                        "InstrumentName": "OPTIDX" ,# Buy/Sell
                        "Signal": str(SquareOffAction).capitalize(),
                        "ExpiryDate": str(ExpiryDate),
                        "ExpiryDateForOdin": str(ChangeExpiryDateFormat(ExpiryDate)),
                        "StrikeType": str(StrikeType),  # CE/PE
                        "StrikePrice": str(StrikePrice),
                        "LTP": str(LastTradingPrice),
                        "Leg": str(Leg),  # 1 / 2 / 3 / 4
                        "TargetPrice": "0.00",
                        "StopLossPrice": "0.00"
                    }

                    data = json.dumps(data)

                    req = requests.post(url, data, headers=headers)
                    response = json.loads(req.text)
                    MAX_TRADE_COUNT += 1

                    try:
                        if response and response['success']:
                            UpdateExitPrice(Leg, LastTradingPrice, logs)

                            UpdateStopLossFlag(Leg,logs)
                       
                        logs.info('Leg : %s, Exit Order Request Placed,  For %s %s %s %s %s',
                                  Leg,  SquareOffAction, Symbol, ExpiryDate, StrikePrice, StrikeType,)
                        
                    except:
                        logs.info('Leg : %s, Response : %s', Leg, response)
                        logs.error(str(traceback.format_exc()))

                else:
                    # worst case, break takeing order after max 3 trades
                    logs.warning('Leg : %s, MAX TRADE COUNT EXCEED, For %s %s %s %s %s',
                                 Leg, SquareOffAction, Symbol, ExpiryDate, StrikePrice, StrikeType,)

            # If No Last Trading Price
            else:
              logs.critical('Leg : %s, No Current Market Price for Trade', Leg, )
        
        else:
            leg_details['SquareOffAction'] = None

            # whichever leg stoploss hits we will update the stoploss flag to its initial condition(i.e. Stoplossflag=True)
            # to continue the trade next day from same condition 
            UpdateStopLossFlag(Leg,logs)

            logs.info(f"LEG {Leg} STOPLOSS ALREADY HIT.....")
    
    else:
        logs.info('No details')

    return None
