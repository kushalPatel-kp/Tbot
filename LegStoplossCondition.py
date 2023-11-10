import json
import time
import requests
from GetData import GetFNOSymbolToken
import redis
from UpdateTradeDetails import *
from FormatExpiryDate import ChangeExpiryDateFormat
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

def checkstoploss(Leg_Data, EntryTime, ExitTime, url, logs):

    MAX_TRADE_COUNT = 0
    response = None

    # Stoplossflag = 1 means stoploss flag is True
    # Stoplossflag = 0 means stoploss flag is False

    if Leg_Data:

        Leg = Leg_Data['Leg']
        Symbol = Leg_Data['Symbol']
        ExpiryDate = Leg_Data['ExpiryDate']
        StrikePrice = Leg_Data['StrikePrice']
        StrikeType = Leg_Data['StrikeType']
        SquareOffAction = Leg_Data['SquareOffAction']
        StopLossPrice = Leg_Data['StopLossPrice']
        StoplossFlag = Leg_Data['StoplossFlag']

        if StopLossPrice and StopLossPrice !=0 and StoplossFlag:

            # local, server = "111.90.169.244", "172.20.10.204"
            # Port : 3011:index, 3012:cash, 3013:fno
            #  "Nifty 50", "Nifty Bank" For index
            # redis.Redis(host="111.90.169.244", port=3013, password='')

            r = redis.Redis(host="172.20.10.204", port=3013, password='')   # for server
            # r = redis.Redis(host="111.90.169.244", port=3013, password='')  # for local
            logs.info(f" ====> Redis connection..{r}")

            p = r.pubsub()
            # print("p ===>>", p)

            Token = GetFNOSymbolToken(Symbol, StrikePrice, ExpiryDate, StrikeType)
            p.subscribe(str(Token))
            # print(Token)

            while datetime.now().strftime("%H:%M") >= EntryTime and datetime.now().strftime("%H:%M") < ExitTime:
                try:
                    try:
                        LiveData = p.get_message()

                        if LiveData and type(LiveData['data'])!=int:
                            d = json.loads(LiveData['data'])         
                            CurrentMarketPrice = d['Price']
                            time.sleep(0.001)  # be nice to sever
                        else:
                            time.sleep(0.001)  # be nice to sever
                            continue
                    except:
                        time.sleep(1)
                        print(traceback.format_exc())
                        raise ValueError('No Live price value')

                    print(f"Leg : {Leg} {Symbol} {str(ExpiryDate)} {StrikePrice} {StrikeType}: SL : {round(StopLossPrice,2)} CMP : {CurrentMarketPrice}", end='\r')

                    if CurrentMarketPrice != 0 and CurrentMarketPrice >= StopLossPrice:

                        print(f"********** Leg {Leg} StopLoss Hit **********")

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
                                "LTP": str(CurrentMarketPrice),
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
                                    logs.info('Leg : %s, SL Order Request Placed,  For %s %s %s %s %s at %s',Leg, SquareOffAction, Symbol, ExpiryDate, StrikePrice, StrikeType,CurrentMarketPrice)
                                    
                                    # here once the stoploss is hit we will update the status of stoplossflag from true to false
                                    UpdateStopLosshitFlag(Leg,logs)

                                    # updating stoploss price in the table
                                    UpdateStopLossPrice(Leg, CurrentMarketPrice, logs)
                                    
                                    #updating the exit price(i.e.price at which the stoploss is hit)
                                    UpdateExitPrice(Leg, CurrentMarketPrice, logs)
                                    Leg_Data['SquareOffAction'] = None
                                    
                            except:
                                logs.info('Leg : %s, Response : %s', Leg, response)
                                logs.error(str(traceback.format_exc()))

                        else:
                            # worst case, break takeing order after max 3 trades
                            logs.warning('Leg : %s, MAX TRADE COUNT EXCEED, For %s %s %s %s %s',Leg, SquareOffAction, Symbol, ExpiryDate, StrikePrice, StrikeType,)
                        p.unsubscribe()
                        p.close()
                        r.close()
                except ValueError as Error:
                    print(Error, end='\r')
                except:
                    print(traceback.format_exc())
                    break
                # time.sleep(0.5)
            else:
                p.unsubscribe()
                p.close()
                r.close()

        elif not StoplossFlag:
            Leg_Data['SquareOffAction'] = None
            logs.info(f"LEG {Leg} STOPLOSS ALREADY HIT.....")

    return Leg_Data