import pandas as pd
import fxcmpy
import time
import datetime as dt
from playsound import playsound
from talib import MACD,EMA,STOCH,RSI,ADX,AD
import matplotlib.pyplot as plt
from datetime import timedelta
from pandas.plotting import register_matplotlib_converters
import pymysql
import os
import plotly.graph_objects as go

def connect():

    global con,upcoming_news_dic,opened_possitions_list

    token = '786733bea669469874c5b4f45be1e1766ac9066b'  # real
    con = fxcmpy.fxcmpy(access_token=token, log_level="error",server='real')
    print(con.get_accounts())
    openedCurrency()
    print('OK')
    return con

def openedCurrency():
    global opened_possitions_list
    opened_possitions_list = []
    info = con.get_open_positions(kind=list)
    num = len(info)
    if num != 0:
        for x in range(0, num):
            opened_possitions_list.append(info.iloc[x]['currency'])
    print(opened_possitions_list)

class Run:
    global z
    def __init__(self,symbol):
        self.symbol=symbol
    #EMA-exponential moving average
    #as four hours data candles are not functional from this API provider we build them from one hour data candles
    def dataH4(self):
        dataH1 = con.get_candles(self.symbol, period='H1', number=2000)
        for x in range(24):
            timestamp = dataH1.index[-1]
            Hour = timestamp.hour
            if (Hour - 1) % 4 == 0:
                break
            else:
                dataH1 = dataH1.drop(dataH1.index[-1])
        for x in range(24):
            timestamp = dataH1.index[0]
            Hour = timestamp.hour
            if (Hour - 1) % 4 == 0:
                break
            else:
                dataH1 = dataH1.drop(dataH1.index[0])
        num = int(len(dataH1) / 4)
        dataH4 = pd.DataFrame(columns=['bidopen', 'bidclose', 'bidhigh', 'bidlow'])
        DataList = []
        for x in range(num):
            if len(dataH1) <= 4:
                break
            for d in range(10):
                L = dataH1.index[0].hour
                if L == 2 or L == 3 or L == 4 or L == 6 or L == 7 or L == 8 or L == 10 or L == 11 or L == 12 or L == 14 \
                        or L == 15 or L == 16 or L == 18 or L == 19 or L == 20 or L == 22 or L == 23 or L == 0:
                    dataH1 = dataH1.drop(dataH1.index[0])
                else:
                    break
            slice = dataH1[:4]
            dataH1 = dataH1.drop(dataH1.index[:4])
            open = slice['bidopen'][0]
            close = slice['bidclose'][-1]
            high = slice['bidhigh'].max()
            low = slice['bidlow'].min()
            timestamp = slice.index[0]
            index = pd.date_range(timestamp, periods=1)
            Data = {'bidopen': open, 'bidclose': close, 'bidhigh': high, 'bidlow': low}
            DataList.append(Data)
            dataNEW = pd.DataFrame(Data, columns=['bidopen', 'bidclose', 'bidhigh', 'bidlow'], index=index)
            dataH4 = dataH4.append(dataNEW)
        ema50H4 = EMA(dataH4['bidclose'], timeperiod=50)
        ema200H4 = EMA(dataH4['bidclose'], timeperiod=200)
        self.dataH4 = dataH4
        self.ema50H4 = ema50H4
        self.ema200H4 = ema200H4
    def showH4(self):
        open_data = self.dataH4['bidopen']
        high_data = self.dataH4['bidhigh']
        low_data = self.dataH4['bidlow']
        close_data = self.dataH4['bidclose']
        hix = []
        for c in range(len(self.dataH4)):
            hix.append(c)
        fig = go.Figure(data=[go.Candlestick(open=open_data, high=high_data, low=low_data, close=close_data)])
        fig.update_layout(title=go.layout.Title(text=self.symbol, xref="paper", x=0))
        fig.add_trace(go.Scatter(x=hix, y=self.ema50H4, name="EMA_50"))
        fig.add_trace(go.Scatter(x=hix, y=self.ema200H4, name="EMA_200"))
        fig.show()
    def killH4(self):
        del self.dataH4
        del self.ema50H4
        del self.ema200H4
    def dataH1(self):
        dataH1 = con.get_candles(self.symbol, period='H1', number=1000)
        ema50H1 = EMA(dataH1['bidclose'], timeperiod=50)
        ema200H1 = EMA(dataH1['bidclose'], timeperiod=200)
        rsi = RSI(dataH1['bidclose'],timeperiod=6)
        self.dataH1 = dataH1
        self.ema50H1 = ema50H1
        self.ema200H1 = ema200H1
        self.rsiH1=rsi
    def killH1(self):
        del self.dataH1
        del self.ema50H1
        del self.ema200H1
        del self.rsiH1
    def data30(self):
        data30 = con.get_candles(self.symbol, period='m30', number=500)
        ema50m30 = EMA(data30['bidclose'], timeperiod=50)
        ema200m30 = EMA(data30['bidclose'], timeperiod=200)
        rsi = RSI(data30['bidclose'], timeperiod=6)
        self.data30 = data30
        self.ema50m30 = ema50m30
        self.ema200m30 = ema200m30
        self.rsi30 = rsi
    def kill30(self):
        del self.data30
        del self.ema50m30
        del self.ema200m30
        del self.rsi30
    def data15(self):
        data15 = con.get_candles(self.symbol, period='m15', number=500)
        ema50m15 = EMA(data15['bidclose'], timeperiod=50)
        ema200m15 = EMA(data15['bidclose'], timeperiod=200)
        rsi = RSI(data15['bidclose'], timeperiod=6)
        self.data15 = data15
        self.ema50m15 = ema50m15
        self.ema200m15 = ema200m15
        self.rsi15=rsi
    def kill15(self):
        del self.data15
        del self.ema50m15
        del self.ema200m15
        del self.rsi15
    def data5(self):
        data5 = con.get_candles(self.symbol, period='m5', number=1000)
        ema50m5 = EMA(data5['bidclose'], timeperiod=50)
        ema200m5 = EMA(data5['bidclose'], timeperiod=200)
        rsi = RSI(data5['bidclose'], timeperiod=6)
        self.data5 = data5
        self.ema3m5 = EMA(data5['bidclose'], timeperiod=3)
        self.ema50m5 = ema50m5
        self.ema200m5 = ema200m5
        self.rsi5=rsi
    def kill5(self):
        del self.data5
        del self.ema50m5
        del self.ema200m5
        del self.rsi5
    def data1(self):
        data1 = con.get_candles(self.symbol, period='m1', number=500)
        ema50m1 = EMA(data1['bidclose'], timeperiod=50)
        ema200m1 = EMA(data1['bidclose'], timeperiod=200)
        rsi = RSI(data1['bidclose'], timeperiod=6)
        self.data1 = data1
        self.ema10m1 = EMA(data1['bidclose'], timeperiod=10)
        self.ema50m1 = ema50m1
        self.ema200m1 = ema200m1
        self.rsi1=rsi
    def kill1(self):
        del self.data1
        del self.ema50m1
        del self.ema200m1
        del self.rsi1
    def count(self,timeframe):
        do=None
        if timeframe==15:
            data=self.data15
        elif timeframe==30:
            data=self.data30
        elif timeframe==60:
            data=self.dataH1
        elif timeframe==240:
            data=self.dataH4
        data['ema50'] = EMA(data['bidclose'], timeperiod=50)
        data['ema200'] = EMA(data['bidclose'], timeperiod=200)
        data['cross'] = 0
        data['count'] = 0
        data['uptrend'] = 0
        data['downtrend'] = 0
        count = 0
        for x in range(0, len(data)):
            if data['ema50'][x - 1] > data['ema200'][x - 1] and data['ema50'][x] < data['ema200'][x]:
                a = data.index[x]
                data.at[a, 'cross'] = -1
            if data['ema50'][x - 1] < data['ema200'][x - 1] and data['ema50'][x] > data['ema200'][x]:
                a = data.index[x]
                data.at[a, 'cross'] = 1
        for x in range(0, len(data)):
            if data['ema50'][x] > data['ema200'][x]:
                a = data.index[x]
                data.at[a, 'uptrend'] = 1
            if data['ema50'][x] < data['ema200'][x]:
                a = data.index[x]
                data.at[a, 'downtrend'] = 1
        for xor in range(0, len(data)):
            if data['cross'][xor] == 1:
                pi = 8
                for z in range(xor + 1, len(data)):
                    pi += 1
                    if data['uptrend'][z] == 1 and pi >= 8:
                        if data['bidlow'][z - 2] < data['ema50'][z - 2] and data['bidlow'][z] > data['ema200'][z] \
                                and data['bidlow'][z - 1] > data['ema200'][z - 1] and data['bidlow'][z - 2] > \
                                data['ema200'][z - 2]:
                            if data['bidclose'][z] > data['ema50'][z] and data['bidopen'][z] > data['ema50'][z]:
                                count += 10
                                a = data.index[z]
                                data.at[a, 'count'] = count
                                pi = 0
                    if data['uptrend'][z] == 0:
                        xor = z
                        count = 0
                        break
                    else:
                        continue
        for xox in range(0, len(data)):
            if data['cross'][xox] == -1:
                pi = 8
                for z in range(xox + 1, len(data)):
                    pi += 1
                    if data['downtrend'][z] == 1 and pi >= 8:
                        if data['bidhigh'][z - 2] > data['ema50'][z - 2] and data['bidhigh'][z - 1] < data['ema200'][
                            z - 1] \
                                and data['bidhigh'][z - 2] < data['ema200'][z - 2] and data['bidhigh'][z - 3] < \
                                data['ema200'][z - 3]:
                            if data['bidclose'][z] < data['ema50'][z] and data['bidopen'][z] < data['ema50'][z]:
                                count += 10
                                a = data.index[z]
                                data.at[a, 'count'] = count
                                pi = 0
                    if data['downtrend'][z] == 0:
                        xox = z
                        count = 0
                        break
                    else:
                        continue
        #print(data[11:])
        for x in range(-1, -len(data), -1):
            if data['count'][x] != 0:
                if data['count'][x] >= 30:
                    do=False
                    print('action is NOT allowed')
                    break
                elif data['count'][x] < 30:
                    do=True
                    print('action is allowed')
                    break
        return do
    def Pivot(self):
        week= con.get_candles(self.symbol, period='W1', number=20)
        d = con.get_candles(self.symbol, period='D1', number=20)
        index=-1
        index1=-1
        Pivotpoint = (d['bidhigh'][index] + d['bidlow'][index] + d['bidclose'][index]) / 3
        First_resistance_R1 = (2 * Pivotpoint) - d['bidlow'][index]
        First_support_S1 = (2 * Pivotpoint) - d['bidhigh'][index]
        Second_resistance_R2 = Pivotpoint + (d['bidhigh'][index] - d['bidlow'][index])
        Second_support_S2 = Pivotpoint - (d['bidhigh'][index] - d['bidlow'][index])
        Third_resistance_R3 = d['bidhigh'][index] + (2 * (Pivotpoint - d['bidlow'][index]))
        Third_support_S3 = d['bidlow'][index] - ((d['bidhigh'][index] - Pivotpoint) * 2)
        WPivotpoint = (week['bidhigh'][index1] + week['bidlow'][index1] + week['bidclose'][index1]) / 3
        WFirst_resistance_R1 = (2 * Pivotpoint) - week['bidlow'][index1]
        WFirst_support_S1 = (2 * Pivotpoint) - week['bidhigh'][index1]
        WSecond_resistance_R2 = Pivotpoint + (week['bidhigh'][index1] - week['bidlow'][index1])
        WSecond_support_S2 = Pivotpoint - (week['bidhigh'][index1] - week['bidlow'][index1])
        WThird_resistance_R3 = week['bidhigh'][index1] + (2 * (Pivotpoint - week['bidlow'][index1]))
        WThird_support_S3 = week['bidlow'][index1] - ((week['bidhigh'][index1] - Pivotpoint) * 2)
        print(self.symbol)
        print('Daily Pivot')
        print('')
        print('PP  : ' + str(Pivotpoint))
        print('R1  : ' + str(First_resistance_R1))
        print('R2  : ' + str(Second_resistance_R2))
        print('R3  : ' + str(Third_resistance_R3))
        print('S1  : ' + str(First_support_S1))
        print('S2  : ' + str(Second_support_S2))
        print('S3  : ' + str(Third_support_S3))
        print('')
        print('Weekly Pivot')
        print('')
        print('PP  : ' + str(WPivotpoint))
        print('R1  : ' + str(WFirst_resistance_R1))
        print('R2  : ' + str(WSecond_resistance_R2))
        print('R3  : ' + str(WThird_resistance_R3))
        print('S1  : ' + str(WFirst_support_S1))
        print('S2  : ' + str(WSecond_support_S2))
        print('S3  : ' + str(WThird_support_S3))
        self.Pivotpoint =Pivotpoint
        self.First_resistance_R1 =First_resistance_R1
        self.First_support_S1 =First_support_S1
        self.Second_resistance_R2 =Second_resistance_R2
        self.Second_support_S2 =Second_support_S2
        self.Third_resistance_R3 =Third_resistance_R3
        self.Third_support_S3 = Third_support_S3
        self.WPivotpoint = WPivotpoint
        self.WFirst_resistance_R1 = WFirst_resistance_R1
        self.WFirst_support_S1 = WFirst_support_S1
        self.WSecond_resistance_R2 = WSecond_resistance_R2
        self.WSecond_support_S2 = WSecond_support_S2
        self.WThird_resistance_R3 = WThird_resistance_R3
        self.WThird_support_S3 = WThird_support_S3
    def PivotEma(self):
        d=self.data30
        A_D = AD(d['bidhigh'], d['bidlow'], d['bidclose'], d['tickqty'])
        A_DEma = EMA(A_D, timeperiod=200)
        ema3 = EMA(d['bidclose'], timeperiod=3)
        self.AD = A_D
        self.ADEma = A_DEma
        self.ema3 = ema3
    def PivotEntry(self,offer):
            limiter=0.001
            dist=0.00025
            for x in range(len(offer)):
                if offer.iloc[x]['currency'] == self.symbol:
                    spread = offer.iloc[x]['spread']
                    spread=spread/10000
            if self.symbol == 'GBP/JPY' or self.symbol == 'USD/JPY' or self.symbol == 'AUD/JPY' \
                    or self.symbol == 'CHF/JPY' or self.symbol == 'EUR/JPY'or self.symbol=='CAD/JPY':
                dist = dist * 100
                spread=spread*100
                limiter=limiter*100
            stop_buy = self.Pivotpoint- ((self.Pivotpoint-self.First_support_S1)/3)
            limit_buy = self.First_resistance_R1-dist-spread
            stop_sell = self.Pivotpoint+((self.First_resistance_R1-self.Pivotpoint)/3)
            limit_sell = self.First_support_S1+dist+spread
            limiter_buy=limit_buy-self.data30['bidclose'][-1]
            limiter_sell=self.data30['bidclose'][-1]-limit_sell
            print(str(limiter_buy)+'   razstoqnie za buy')
            print(str(limiter_sell) + '   razstoqnie za sell')
            if (self.ema3[-3]<self.Pivotpoint and self.ema3[-2]>self.Pivotpoint) or\
                    (self.ema3[-2]<self.Pivotpoint and self.ema3[-1]>self.Pivotpoint) :
                if self.AD[-1]>self.ADEma[-1]:
                    if self.data30['bidclose'][-1]>self.Pivotpoint and limiter_buy>=limiter:
                        opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=False, limit=limit_buy,
                                               stop=stop_buy)
                        print(self.symbol+'                                                  Pivot Entry Buy')
                        playsound('protosWarp.mp3')
            if (self.ema3[-3]>self.Pivotpoint and self.ema3[-2]<self.Pivotpoint) or\
                    (self.ema3[-2]>self.Pivotpoint and self.ema3[-1]<self.Pivotpoint) :
                if self.AD[-1]<self.ADEma[-1]:
                    if self.data30['bidclose'][-1]<self.Pivotpoint and limiter_sell>=limiter:
                        opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=False, limit=limit_sell,
                                               stop=stop_sell)
                        playsound('protosWarp.mp3')
                        print(self.symbol + '                                                Pivot Entry Sell')
    def supres5( self, min_touches=2, stat_likeness_percent=1.5, bounce_percent=15): #data_type variable
        print('~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ')
        print(self.symbol)
        high=self.data5['bidhigh']
        low=self.data5['bidlow']
        supList=[]
        resList=[]
        # Setting default values for support and resistance to None
        sup = None
        res = None
        # Identifying local high and local low
        maxima = high.max()
        minima = low.min()
        rawdata=self.data5
        maxi = rawdata.index[rawdata['bidhigh'] == maxima].tolist()
        mini = rawdata.index[rawdata['bidlow'] == minima].tolist()
        newdata = rawdata.drop(mini)
        newdata = newdata.drop(maxi)
        # Calculating distance between max and min (total price movement)
        move_range = maxima - minima
        # Calculating bounce distance and allowable margin of error for likeness
        move_allowance = move_range * (stat_likeness_percent / 100)
        bounce_distance = move_range * (bounce_percent / 100)
        # Test resistance by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for x in range(0, len(high)):
            if abs(maxima - high[x]) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                resList.append(self.data5.index[x])
                awaiting_bounce = True
            elif abs(maxima - high[x]) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            res = maxima
            print('resistance-     ' + str(touchdown))
        # Test support by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for x in range(0, len(low)):
            if abs(low[x] - minima) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                supList.append(self.data5.index[x])
                awaiting_bounce = True
            elif abs(low[x] - minima) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            sup = minima
            print('support-    ' + str(touchdown))
        return sup, res,supList,resList,newdata,maxima,minima
    def supres2(self, newdata,min_touches=2, stat_likeness_percent=1.5, bounce_percent=15):
        high=newdata['bidhigh']
        low=newdata['bidlow']
        supList = []
        resList = []
        # Setting default values for support and resistance to None
        sup = None
        res = None
        # Identifying local high and local low
        maxima = high.max()
        minima = low.min()
        # Calculating distance between max and min (total price movement)
        move_range = maxima - minima
        # Calculating bounce distance and allowable margin of error for likeness
        move_allowance = move_range * (stat_likeness_percent / 100)
        bounce_distance = move_range * (bounce_percent / 100)
        # Test resistance by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for x in range(0, len(high)):
            if abs(maxima - high[x]) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                resList.append(self.data5.index[x])
                awaiting_bounce = True
            elif abs(maxima - high[x]) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            res = maxima
            print('res' + str(touchdown))
            print(resList)
        # Test support by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for x in range(0, len(low)):
            if abs(low[x] - minima) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                supList.append(self.data5.index[x])
                awaiting_bounce = True
            elif abs(low[x] - minima) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            sup = minima
            print('sup' + str(touchdown))
            print(supList)
        return sup, res,maxima,minima
    def supportEntry(self,supList,minima):#
        Orders=False
        dist = 0.001
        stop = -10
        limit = 10
        if self.symbol == 'GBP/JPY' or self.symbol == 'USD/JPY' or self.symbol == 'AUD/JPY' \
                or self.symbol == 'CHF/JPY' or self.symbol == 'EUR/JPY'or self.symbol=='CAD/JPY':
            dist = dist * 100
        EntryBuyPoint = minima + dist
        EntrySellPoint = minima - dist
        #limitPointBuy = EntryBuyPoint + limit
        #stopPointBuy = EntryBuyPoint - stop
        #limitPointSell = EntrySellPoint - limit
        #stopPointSell = EntrySellPoint + stop
        timenow=dt.datetime.now()
        expiration_time=str(timenow-timedelta(hours=1)+timedelta(minutes=10))
        if ((timenow-timedelta(hours=1))-supList[-1])<=timedelta(minutes=5) and len(supList)>=2:
            order = con.create_entry_order(symbol=self.symbol, is_buy=True,
                                           amount=1, limit=limit,
                                           is_in_pips=True,
                                           time_in_force='GTD', expiration=expiration_time,
                                           rate=EntryBuyPoint, stop=stop, trailing_step=None,
                                           trailing_stop_step=None)
            order = con.create_entry_order(symbol=self.symbol, is_buy=False,
                                           amount=1, limit=limit,
                                           is_in_pips=True,
                                           time_in_force='GTD', expiration=expiration_time,
                                           rate=EntrySellPoint, stop=stop, trailing_step=None,
                                           trailing_stop_step=None)
            f = open("BotLog.txt", "a")
            f.write(str(timenow) + '\n')
            f.write(self.symbol + " Support Entry!! \n")
            f.write(str(supList)+'\n')
            f.write(str(minima)+'\n')
            f.write('-------------------------------------------\n')
            f.close()
            print('Support Entry!!!!!!!!!!!!!!')
            Orders=True
            return Orders
    def resistanceEntry(self,resList,maxima):
        Orders=False
        dist = 0.001
        stop=-10
        limit=10
        if self.symbol == 'GBP/JPY' or self.symbol == 'USD/JPY' or self.symbol == 'AUD/JPY' \
                or self.symbol == 'CHF/JPY' or self.symbol == 'EUR/JPY' or self.symbol == 'CAD/JPY':
            dist = dist * 100
        EntryBuyPoint = maxima + dist
        EntrySellPoint = maxima - dist
        timenow=dt.datetime.now()
        expiration_time = str(timenow + timedelta(minutes=10))
        if ((timenow-timedelta(hours=1))-resList[-1])<=timedelta(minutes=5) and len(resList)>=2:
            order = con.create_entry_order(symbol=self.symbol, is_buy=True,
                                           amount=1, limit=limit,
                                           is_in_pips=True,
                                           time_in_force='GTD', expiration=expiration_time,
                                           rate=EntryBuyPoint, stop=stop, trailing_step=None,
                                           trailing_stop_step=None)
            order = con.create_entry_order(symbol=self.symbol, is_buy=False,
                                           amount=1, limit=limit,
                                           is_in_pips=True,
                                           time_in_force='GTD', expiration=expiration_time,
                                           rate=EntrySellPoint, stop=stop, trailing_step=None,
                                           trailing_stop_step=None)
            f = open("BotLog.txt", "a")
            f.write(str(timenow) + '\n')
            f.write(self.symbol + " Resistance Entry!! \n")
            f.write(str(resList)+'\n')
            f.write(str(maxima)+'\n')
            f.write('-----------------------------------------------\n')
            f.close()
            print('Resistance Entry!!!!!!!!!!!!!!')
            Orders=True
            return Orders
    def AlgoCross(self):
        if self.ema50H1[-2]<self.ema200H1[-2] and self.ema50H1[-1]>self.ema200H1[-1]:
            opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=180,
                                       time_in_force='GTC',
                                       order_type='AtMarket', is_in_pips=True, limit=70,
                                       stop=-35)
        if self.ema50H1[-2]>self.ema200H1[-2] and self.ema50H1[-1]<self.ema200H1[-1]:
            opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=180,
                                       time_in_force='GTC',
                                       order_type='AtMarket', is_in_pips=True, limit=70,
                                       stop=-35)
    def AlgoH4(self):
        timenow=dt.datetime.now()
        do = True
        if self.symbol in opened_possitions_list:
            do = False
        xSell=None
        xBuy=None
        ready1Hb=False
        ready1Hs=False
        dist = 0.0035
        if self.symbol == 'GBP/JPY' or self.symbol == 'USD/JPY' or self.symbol == 'AUD/JPY' \
                or self.symbol == 'CHF/JPY' or self.symbol == 'EUR/JPY' or self.symbol=='CAD/JPY':
            dist = dist * 100
        if (self.ema200H4[-1] - self.ema50H4[-1])>=dist and self.dataH4['bidclose'][-1]<self.ema200H4[-1]:
            print('one')
            xSell=True
            for x in range(-15,0):
                if self.dataH4['bidhigh'][x]>self.ema50H4[x]:
                    ready1Hs=False
                    break
                else:
                    ready1Hs=True
            if (self.dataH4['bidhigh'][-3] > self.ema50H4[-3] or self.dataH4['bidhigh'][-2] > self.ema50H4[-2]) and \
                    self.ema50H4[-1]<self.ema50H4[-3]<self.ema50H4[-5]<self.ema50H4[-7]:
                print('two')
                    #and (self.rsiH4[-3] > 70 or self.rsiH4[-2] > 70 or self.rsiH4[-1] > 70):
                if self.dataH4['bidopen'][-3] < self.dataH4['bidclose'][-3] and self.dataH4['bidopen'][-2] > \
                        self.dataH4['bidclose'][-2] and \
                        self.dataH4['bidopen'][-1] > self.dataH4['bidclose'][-1]:
                    print('three')
                    if do:
                        print('four')
                        opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=50,
                                               stop=-50)
                        opened_possitions_list.append(self.symbol)
                        print(self.symbol+'  SELL  H4 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        f = open("BotLog.txt", "a")
                        f.write(str(timenow)+'\n')
                        f.write(self.symbol+"   H4  SELL \n"  )
                        f.write('------------------------------------------- \n')
                        f.close()
        if (self.ema50H4[-1] - self.ema200H4[-1])>=dist and self.dataH4['bidclose'][-1]>self.ema200H4[-1] :
            xBuy=True
            for x in range(-15,0):
                if self.dataH4['bidlow'][x]<self.ema50H4[x]:
                    ready1Hb=False
                    break
                else:
                    ready1Hb=True
            #print('ready  M30    '+str(ready30))
            if (self.dataH4['bidlow'][-3] < self.ema50H4[-3] or self.dataH4['bidlow'][-2] < self.ema50H4[-2]) and\
                    self.ema50H4[-1]>self.ema50H4[-3]>self.ema50H4[-5]>self.ema50H4[-7]:
                if self.dataH4['bidopen'][-3] > self.dataH4['bidclose'][-3] and self.dataH4['bidopen'][-2] < \
                        self.dataH4['bidclose'][-2] and \
                        self.dataH4['bidopen'][-1] < self.dataH4['bidclose'][-1]:
                    if do:
                        opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=50,
                                               stop=-50)
                        opened_possitions_list.append(self.symbol)
                        print(self.symbol+'  BUY   H4 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        f = open("BotLog.txt", "a")
                        f.write(str(timenow)+'\n')
                        f.write(self.symbol + "   H4  BUY\n")
                        f.write('-------------------------------------------\n')
                        f.close()
        return xBuy,xSell,ready1Hb,ready1Hs
    def AlgoH1(self,ready1Hb,ready1Hs,count):
        timenow=dt.datetime.now()
        do=True
        dist=0.0020
        if self.symbol in opened_possitions_list:
            do=False
        ready30b=False
        ready30s=False
        if self.symbol == 'GBP/JPY' or self.symbol == 'USD/JPY' or self.symbol == 'AUD/JPY' \
                or self.symbol == 'CHF/JPY' or self.symbol == 'EUR/JPY'or self.symbol=='CAD/JPY':
            dist = dist * 100
        if ready1Hs:
            if (self.ema200H1[-1] - self.ema50H1[-1])>=dist and (self.ema200H4[-1] - self.ema50H4[-1])>=dist and self.dataH1['bidclose'][-1]<self.ema200H1[-1]:
                for x in range(-15,0):
                    if self.dataH1['bidhigh'][x]>self.ema50H1[x]:
                        ready30s=False
                        break
                    else:
                        ready30s=True
                if (self.dataH1['bidhigh'][-3] > self.ema50H1[-3] or self.dataH1['bidhigh'][-2] > self.ema50H1[-2]) \
                        and (self.rsiH1[-3] > 60 or self.rsiH1[-2] > 60 or self.rsiH1[-1] > 60):
                    if self.dataH1['bidopen'][-3] < self.dataH1['bidclose'][-3] and self.dataH1['bidopen'][-2] > \
                            self.dataH1['bidclose'][-2] and \
                            self.dataH1['bidopen'][-1] > self.dataH1['bidclose'][-1]:
                        if do and count:
                            opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1,
                                                   time_in_force='GTC',
                                                   order_type='AtMarket', is_in_pips=True, limit=25,
                                                   stop=-20)
                            opened_possitions_list.append(self.symbol)
                            print(self.symbol+'  SELL  H1 $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            f = open("BotLog.txt", "a")
                            f.write(str(timenow)+'\n')
                            f.write(self.symbol + "   H1  SELL\n")
                            f.write('-------------------------------------------\n')
                            f.close()
        if ready1Hb :
            if (self.ema50H1[-1] - self.ema200H1[-1])>=dist and (self.ema50H4[-1] - self.ema200H4[-1])>=dist and self.dataH1['bidclose'][-1]>self.ema200H1[-1] :
                for x in range(-15,0):
                    if self.dataH1['bidlow'][x]<self.ema50H1[x]:
                        ready30b=False
                        break
                    else:
                        ready30b=True
                #print('ready  M30    '+str(ready30))
                if (self.dataH1['bidlow'][-3] < self.ema50H1[-3] or self.dataH1['bidlow'][-2] < self.ema50H1[-2]) \
                        and (self.rsiH1[-3] < 40 or self.rsiH1[-2] < 40 or self.rsiH1[-1] < 40):
                    if self.dataH1['bidopen'][-3] > self.dataH1['bidclose'][-3] and self.dataH1['bidopen'][-2] < \
                            self.dataH1['bidclose'][-2] and \
                            self.dataH1['bidopen'][-1] < self.dataH1['bidclose'][-1]:
                        if do and count:
                            opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1,
                                                   time_in_force='GTC',
                                                   order_type='AtMarket', is_in_pips=True, limit=25,
                                                   stop=-20)
                            opened_possitions_list.append(self.symbol)
                            print(self.symbol+'  BUY   H1  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            f = open("BotLog.txt", "a")
                            f.write(str(timenow)+'\n')
                            f.write(self.symbol + "   H1  BUY \n")
                            f.write('-------------------------------------------\n')
                            f.close()
        return ready30b,ready30s
    def Algom30(self,ready30b,ready30s,count):
        timenow=dt.datetime.now()
        do = True
        if self.symbol in opened_possitions_list:
            do = False
        ready15b=False
        ready15s=False
        if ready30s:
            if self.ema50m30[-1] < self.ema200m30[-1] and self.ema50H1[-1] < self.ema200H1[-1] and self.data30['bidclose'][-1]<self.ema200m30[-1] :
                for x in range(-17, 0):
                    if self.data30['bidhigh'][x] > self.ema50m30[x]:
                        ready15s = False
                        break
                    else:
                        ready15s = True
                if (self.data30['bidhigh'][-3] > self.ema50m30[-3] or self.data30['bidhigh'][-2] > self.ema50m30[-2]) :
                    if (self.rsi30[-3] > 60 or self.rsi30[-2] > 60 or self.rsi30[-1] > 60):
                        if self.data30['bidopen'][-3] < self.data30['bidclose'][-3] and self.data30['bidopen'][-2] > \
                            self.data30['bidclose'][-2] and \
                            self.data30['bidopen'][-1] > self.data30['bidclose'][-1]:
                            if do and count:
                                opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=20,
                                               stop=-15)
                                opened_possitions_list.append(self.symbol)
                                print(self.symbol+'  M30   SELL   $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                                f = open("BotLog.txt", "a")
                                f.write(str(timenow) + '\n')
                                f.write(self.symbol + "   m30  SELL \n")
                                f.write('-------------------------------------------\n')
                                f.close()
        if ready30b:
            if self.ema50m30[-1] > self.ema200m30[-1] and self.ema50H1[-1] > self.ema200H1[-1] and self.data30['bidclose'][-1]>self.ema200m30[-1]:
                for x in range(-17,0):
                    if self.data30['bidlow'][x]<self.ema50m30[x]:
                        ready15b=False
                        break
                    else:
                        ready15b=True
                if (self.data30['bidlow'][-3] < self.ema50m30[-3] or self.data30['bidlow'][-2] < self.ema50m30[-2]) \
                    and (self.rsi30[-3] < 40 or self.rsi30[-2] < 40 or self.rsi30[-1] < 40):
                    if self.data30['bidopen'][-3] > self.data30['bidclose'][-3] and self.data30['bidopen'][-2] < \
                        self.data30['bidclose'][-2] and \
                        self.data30['bidopen'][-1] < self.data30['bidclose'][-1]:
                        if do and count:
                            opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=20,
                                               stop=-15)
                            opened_possitions_list.append(self.symbol)
                            print(self.symbol+'  M30     BUY    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            f = open("BotLog.txt", "a")
                            f.write(str(timenow) + '\n')
                            f.write(self.symbol + "   m30  BUY \n")
                            f.write('-------------------------------------------\n')
                            f.close()
        return ready15b,ready15s
    def Algom15(self,ready15b,ready15s,count):
        timenow=dt.datetime.now()
        do = True
        if self.symbol in opened_possitions_list:
            do = False
        ready5b=False
        ready5s=False
        if ready15s:
            if self.ema50m15[-1] < self.ema200m15[-1] and self.ema50m30[-1] < self.ema200m30[-1] and self.data15['bidclose'][-1]<self.ema200m15[-1] :
                for x in range(-15, 0):
                    if self.data15['bidhigh'][x] > self.ema50m15[x]:
                        ready5s = False
                        break
                    else:
                        ready5s = True
                if (self.data15['bidhigh'][-3] > self.ema50m15[-3] or self.data15['bidhigh'][-2] > self.ema50m15[-2]) \
                    and (self.rsi15[-3] > 65 or self.rsi15[-2] > 65 or self.rsi15[-1] > 65):
                    if self.data15['bidopen'][-3] < self.data15['bidclose'][-3] and self.data15['bidopen'][-2] > \
                        self.data15['bidclose'][-2] and \
                        self.data15['bidopen'][-1] > self.data15['bidclose'][-1]:
                        if do and count:
                            opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=20,
                                               stop=-15)
                            opened_possitions_list.append(self.symbol)
                            print(self.symbol+'  M15     SELL     $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            f = open("BotLog.txt", "a")
                            f.write(str(timenow) + '\n')
                            f.write(self.symbol + "   m15  SELL \n")
                            f.write('-------------------------------------------\n')
                            f.close()
        if ready15b:
            if self.ema50m15[-1] > self.ema200m15[-1] and self.ema50m30[-1] > self.ema200m30[-1] and self.data15['bidclose'][-1]>self.ema200m15[-1]:
                for x in range(-15,0):
                    if self.data15['bidlow'][x]<self.ema50m15[x]:
                        ready5s=False
                        break
                    else:
                        ready5s=True
                if (self.data15['bidlow'][-3] < self.ema50m15[-3] or self.data15['bidlow'][-2] < self.ema50m15[-2]) \
                    and (self.rsi15[-3] < 35 or self.rsi15[-2] < 35 or self.rsi15[-1] < 35):
                    if self.data15['bidopen'][-3] > self.data15['bidclose'][-3] and self.data15['bidopen'][-2] < \
                        self.data15['bidclose'][-2] and \
                        self.data15['bidopen'][-1] < self.data15['bidclose'][-1]:
                        if do and count:
                            opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=20,
                                               stop=-15)
                            opened_possitions_list.append(self.symbol)
                            print(self.symbol+'  M15  BUY    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            f = open("BotLog.txt", "a")
                            f.write(str(timenow) + '\n')
                            f.write(self.symbol + "   m15  BUY \n")
                            f.write('-------------------------------------------\n')
                            f.close()
        return ready5b,ready5s
    def Algom5(self,ready5b,ready5s):
        timenow=dt.datetime.now()
        do = False
        if self.symbol in opened_possitions_list:
            do = False
        ready1s=False
        ready1b=False
        if ready5s:
            if self.ema50m5[-1] < self.ema200m5[-1] and self.ema50m15[-1] < self.ema200m15[-1] and self.data5['bidclose'][-1]<self.ema200m5[-1] :
                for x in range(-15, 0):
                    if self.data5['bidhigh'][x] > self.ema50m5[x]:
                        ready1s = False
                        break
                    else:
                        ready1s = True
                if (self.data5['bidhigh'][-3] > self.ema50m5[-3] or self.data5['bidhigh'][-2] > self.ema50m5[-2]) :
                    #and (self.rsi5[-3] > 70 or self.rsi5[-2] > 70 or self.rsi5[-1] > 70):
                    if self.data5['bidopen'][-3] < self.data5['bidclose'][-3] and self.data5['bidopen'][-2] > \
                        self.data5['bidclose'][-2] and \
                        self.data5['bidopen'][-1] > self.data5['bidclose'][-1]:
                        if do:
                            opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=20,
                                               stop=-20)
                            opened_possitions_list.append(self.symbol)
                            print(self.symbol+'  M5     SELL    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            f = open("BotLog.txt", "a")
                            f.write(str(timenow) + '\n')
                            f.write(self.symbol + "   m5  SELL \n")
                            f.write('-------------------------------------------\n')
                            f.close()
        if ready5b:
            if self.ema50m5[-1] > self.ema200m5[-1] and self.ema50m15[-1] > self.ema200m15[-1] and self.data5['bidclose'][-1]>self.ema200m5[-1] :
                for x in range(-15,0):
                    if self.data5['bidlow'][x]<self.ema50m5[x]:
                        ready1b=False
                        break
                    else:
                        ready1b=True
                if (self.data5['bidlow'][-3] < self.ema50m5[-3] or self.data5['bidlow'][-2] < self.ema50m5[-2]) :
                    #and (self.rsi5[-3] < 30 or self.rsi5[-2] < 30 or self.rsi5[-1] < 30):
                    if self.data5['bidopen'][-3] > self.data5['bidclose'][-3] and self.data5['bidopen'][-2] < \
                        self.data5['bidclose'][-2] and \
                        self.data5['bidopen'][-1] < self.data5['bidclose'][-1]:
                        if do:
                            opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=20,
                                               stop=-10)
                            opened_possitions_list.append(self.symbol)
                            print(self.symbol+'  M5    BUY    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                            f = open("BotLog.txt", "a")
                            f.write(str(timenow) + '\n')
                            f.write(self.symbol + "   m5  BUY \n")
                            f.write('-------------------------------------------\n')
                            f.close()
        return ready1b,ready1s
    def Algom1(self,p1ready1b,p1ready1s):
        timenow=dt.datetime.now()
        do = False
        if self.symbol in opened_possitions_list:
            do = False
            print(self.symbol + ' still open')
        if p1ready1s and do:
            if self.ema50m1[-1] < self.ema200m1[-1] and self.ema50m15[-1] < self.ema200m15[-1] and self.data1['bidclose'][-1]<self.ema200m1[-1] :
                if self.data1['bidhigh'][-3] > self.ema50m1[-3] or self.data1['bidhigh'][-2] > self.ema50m1[-2]:
                    if self.data1['bidopen'][-3] < self.data1['bidclose'][-3] and self.data1['bidopen'][-2] > \
                        self.data1['bidclose'][-2] and \
                        self.data1['bidopen'][-1] > self.data1['bidclose'][-1]:
                        opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=2,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=10,
                                               stop=-10)
                        opened_possitions_list.append(self.symbol)
                        print(self.symbol+'  SELL  M1    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        f = open("BotLog.txt", "a")
                        f.write(str(timenow) + '\n')
                        f.write(self.symbol + "   m1  SELL \n")
                        f.write('-------------------------------------------\n')
                        f.close()
        if p1ready1b and do:
            if self.ema50m1[-1] > self.ema200m1[-1] and self.ema50m15[-1] > self.ema200m15[-1] and self.data1['bidclose'][-1]>self.ema200m1[-1] :
                if self.data1['bidlow'][-3] < self.ema50m1[-3] or self.data1['bidlow'][-2] < self.ema50m1[-2]:
                    if self.data1['bidopen'][-3] > self.data1['bidclose'][-3] and self.data1['bidopen'][-2] < \
                        self.data1['bidclose'][-2] and \
                        self.data1['bidopen'][-1] < self.data1['bidclose'][-1]:
                        opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=2,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=10,
                                               stop=-10)
                        opened_possitions_list.append(self.symbol)
                        print(self.symbol+'  BUY  M1    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
                        f = open("BotLog.txt", "a")
                        f.write(str(timenow) + '\n')
                        f.write(self.symbol + "   m1  BUY \n")
                        f.write('-------------------------------------------\n')
                        f.close()
    def Algo_m1_ema10(self,p1ready1b,p1ready1s):
        timenow=dt.datetime.now()
        do=None
        if self.symbol in opened_possitions_list:
            do = False
            print(self.symbol + ' still open')
        if p1ready1s and do:
            if self.ema3m5[-1]<self.ema50m5[-1]<self.ema200m5[-1]:
                if self.ema10m1[-1]<self.ema50m1[-1]<self.ema200m1[-1]:
                    opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=50,
                                               stop=-10)
                    tradeId=con.get_open_trade_ids()[-1]
                    listi=[(str(timenow),str(tradeId),'SELL',self.symbol)]
                    DB.insertTrade(listi)
                    opened_possitions_list.append(self.symbol)
        if p1ready1b and do:
            if self.ema3m5[-1]>self.ema50m5[-1]>self.ema200m5[-1]:
                if self.ema10m1[-1]>self.ema50m1[-1]>self.ema200m1[-1]:
                    opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1,
                                               time_in_force='GTC',
                                               order_type='AtMarket', is_in_pips=True, limit=50,
                                               stop=-10)
                    tradeId = con.get_open_trade_ids()[-1]
                    listi = [(str(timenow), str(tradeId), 'BUY', self.symbol)]
                    DB.insertTrade(listi)
                    opened_possitions_list.append(self.symbol)
    def close_m1(self,isBuy,tradeId):
        if isBuy==False:
            if self.ema10m1[-1] > self.ema50m1[-1]:
                con.close_trade(trade_id=int(tradeId),amount=1)
                DB.delTrade('algo_m1',tradeId)
        if isBuy==True:
            if self.ema10m1[-1] < self.ema50m1[-1]:
                con.close_trade(trade_id=int(tradeId),amount=1)
                DB.delTrade('algo_m1', tradeId)
