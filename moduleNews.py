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
from moduleRun import connect

opened_possitions_list=[]
upcoming_news_dic={}
change_of_price_list=[0, 0, 0, 0, 0, 0]

upcoming_news_dic[dt.datetime(2019, 9, 13, 13, 20, 0)] = 'EUR/USD', 'USD/JPY', 'USD/CAD', 'GBP/USD', 'AUD/USD', 'USD/CHF'
upcoming_news_dic[dt.datetime(2019,9,12,12,30,0)] = 'EUR/GBP','EUR/USD','EUR/CHF','EUR/JPY','EUR/AUD','EUR/CAD'
upcoming_news_dic[dt.datetime(2019,9,10,15,14,0) ] = 'GBP/USD','EUR/GBP','GBP/CHF','GBP/CAD','GBP/NZD', 'GBP/AUD','GBP/JPY'
print('                      -------------NEWS--------------')
print(upcoming_news_dic)
print('                      -------------------------------')


class News:
    def __init__(self,symbol):
        self.symbol=symbol

    def news_placing_orders(self):
        current_price=self.data['Bid'][-1]
        distance_between_current_price_and_target_limit = 0.0015
        stop = -10
        limit = 40
        if self.symbol == 'GBP/JPY' or self.symbol == 'USD/JPY' or self.symbol == 'AUD/JPY' \
                or self.symbol == 'CHF/JPY' or self.symbol == 'EUR/JPY' or self.symbol == 'CAD/JPY':
            distance_between_current_price_and_target_limit = distance_between_current_price_and_target_limit * 100
        EntryBuyPoint = current_price + distance_between_current_price_and_target_limit
        EntrySellPoint = current_price - distance_between_current_price_and_target_limit
        timenow = dt.datetime.now()
        expiration_time_of_trade = str(timenow + timedelta(minutes=35)-timedelta(hours=1))
        order = con.create_entry_order(symbol=self.symbol, is_buy=True,
                                           amount=1, limit=limit,
                                           is_in_pips=True,
                                           time_in_force='GTD', expiration=expiration_time_of_trade,
                                           rate=EntryBuyPoint, stop=stop, trailing_step=None,
                                           trailing_stop_step=1)
        order = con.create_entry_order(symbol=self.symbol, is_buy=False,
                                           amount=1, limit=limit,
                                           is_in_pips=True,
                                           time_in_force='GTD', expiration=expiration_time_of_trade,
                                           rate=EntrySellPoint, stop=stop, trailing_step=None,
                                           trailing_stop_step=1)
        insert_in_database_list = [(str(timenow), 'NONE', 'BUY', self.symbol,'NEWS')]
        DB.insert_news(insert_in_database_list)
        insert_in_database_list = [(str(timenow), 'NONE', 'SELL', self.symbol,'NEWS')]
        DB.insert_news(insert_in_database_list)
        Orders = True
        return Orders
    def subscribe(self):
        con.subscribe_market_data(self.symbol)
    def get_prices(self):
        self.data = con.get_prices(self.symbol)
    def kill(self):
        del self.data
    def killObj(self):
        print('.      .')
        print(self.symbol)
        del self.symbol
    def news_creating_lists(self,openedBUY,openedSELL):
        self.dic_for_saving={}
        self.dynamic_difference_in_price_list=[]
        self.openedBUY=openedBUY
        self.openedSELL=openedSELL
    def append(self,calc):
        self.dynamic_difference_in_price_list.append(self.data['Bid'][-1])
        self.dic_for_saving[time.strftime("%H:%M:%S")]=([str(self.data['Bid'][-1])+'  '+'[-1][-9] 10 :   '+str(calc)])
        print(self.data['Bid'][-1])
        if len(self.dynamic_difference_in_price_list)<10:
            for x in range(10):
                self.dynamic_difference_in_price_list.append(self.data['Bid'][-1])
        subscription_symbol_status_boolean = con.is_subscribed(self.symbol)
        return subscription_symbol_status_boolean
    def reset_raw(self):
        self.dynamic_difference_in_price_list=[]
    def saving_data_files(self):
        symbol=self.symbol.split('/')
        sym=symbol[0]+symbol[1]
        timeMark=sym+time.strftime("%mo%d__%Ho%M")
        f = open('NEWS REG/'+timeMark+'.txt', "w")
        for x,y in self.dic_for_saving.items():
            f.write(str(x)+' '+str(y)+'\n')
        f.write('---------------------------------------------------------------------------------------------\n')
        f.close()
    def saving_end(self):
        f = open("NewsLog.txt", "a")
        f.write('END\n')
        f.close()
    def analyze(self):
        print(self.symbol)
        minimum_difference_to_activate_trade=0.0011
        currency_coefficient= 1
        if self.symbol == 'GBP/JPY' or self.symbol == 'USD/JPY' or self.symbol == 'AUD/JPY'\
                or self.symbol == 'CHF/JPY' or self.symbol=='EUR/JPY' or self.symbol=='CAD/JPY':
            currency_coefficient = 100
        if (self.dynamic_difference_in_price_list[-9] - self.dynamic_difference_in_price_list[-1])>(minimum_difference_to_activate_trade * currency_coefficient) :
            for x in self.openedBUY:
                if x==self.symbol:
                    con.close_all_for_symbol(self.symbol)
            opentrade = con.open_trade(symbol=self.symbol, is_buy=False, amount=1, time_in_force='GTC',
                                order_type='AtMarket', is_in_pips=True, limit=50, stop=-10,trailing_step=1)
            timenow=dt.datetime.now()
            f = open("BotLog.txt", "a")
            f.write(str(timenow) + '\n')
            f.write(self.symbol + " News Entry!!  Sell.\n")
            f.write('-------------------------------------------\n')
            f.close()
        if (self.dynamic_difference_in_price_list[-1] - self.dynamic_difference_in_price_list[-9]) >(minimum_difference_to_activate_trade * currency_coefficient) :#and (self.raw[-3]- self.raw[-6])>(diff*jump) and (self.raw[-6] - self.raw[-9])>(diff*jump):
            for x in self.openedSELL:
                if x==self.symbol:
                    con.close_all_for_symbol(self.symbol)
            opentrade = con.open_trade(symbol=self.symbol, is_buy=True, amount=1, time_in_force='GTC',
                                       order_type='AtMarket', is_in_pips=True, limit=50, stop=-10, trailing_step=1)
            timenow = dt.datetime.now()
            f = open("BotLog.txt", "a")
            f.write(str(timenow) + '\n')
            f.write(self.symbol + " News Entry!!  Buy.\n")
            f.write('-------------------------------------------\n')
            f.close()
        #print('[-1][-3]1.5 :   ' + str(round(((self.raw[-3]) * (10000/jump)) - ((self.raw[-1]) * (10000/jump)), 1)))
        #print('[-3][-6]1.5 :   ' + str(round(((self.raw[-6]) * (10000/jump)) - ((self.raw[-3]) * (10000/jump)), 1)))
        price_difference=str(round(((self.dynamic_difference_in_price_list[-9]) * (10000 / currency_coefficient)) - ((self.dynamic_difference_in_price_list[-1]) * (10000 / currency_coefficient)), 1))
        print('[-1][-9] 10 :   ' + price_difference)
        print('-----------------------------------')
        return price_difference
def buy_sell_list():
    openedBUY = []
    openedSELL = []
    info = con.get_open_positions(kind=list)
    for x in range(0, len(info)):
        if info.iloc[x]['isBuy'] == True:
            openedBUY.append(info.iloc[x]['currency'])
        if info.iloc[x]['isBuy'] == False:
            openedSELL.append(info.iloc[x]['currency'])
    return openedBUY,openedSELL
def deleting_all_orders():
    orders=con.get_order_ids()
    for x in orders:
        con.delete_order(x)
def delete_orders_from_news(symbol,list_of_orders):
    for x in list_of_orders:
        if x['currency']==symbol:
            con.delete_order(x['orderId'])
def NewsAction():
        list_of_symbols=[]
        currenttime = dt.datetime.now()
        for date_of_news,affected_symbols_in_news in upcoming_news_dic.items():
            if currenttime.day == date_of_news.day and currenttime.hour == date_of_news.hour and currenttime.minute == date_of_news.minute :
                print(currenttime)
                objects_list=[]
                openedBUY,openedSELL=buy_sell_list()
                for x in affected_symbols_in_news:
                    object=News(x)
                    objects_list.append(object)
                list_of_orders,list_of_symbols=orders_list()
                for x in objects_list:
                    delete_orders_from_news(x.symbol,list_of_orders)
                    x.subscribe()
                    x.news_creating_lists(openedBUY,openedSELL)
                    x.get_prices()
                    x.news_placing_orders()
                subscribed_symbols_list=con.get_subscribed_symbols()
                print(subscribed_symbols_list)
                current =currenttime
                while current-currenttime < timedelta(minutes=30):# runs for 30 minutes
                    current = dt.datetime.now()
                    price_difference=''
                    for x in objects_list:
                        print(current.time())
                        x.kill()
                        x.get_prices()
                        x.stuck=x.append(price_difference)
                        print(x.stuck)
                        price_difference=x.analyze()
                        if x.stuck==False:
                            print(x.symbol+'   IS STUCK!')
                            x.reset_raw()
                            x.subscribe()
                    time.sleep(1)
                    if current.second==30:
                        for x in objects_list:
                            list_of_orders,list_of_symbols=orders_list()
                            delete_orders(x.symbol,list_of_orders)
                currenttime = dt.datetime.now()
                print('END     '+str(currenttime))
                for x in objects_list:
                    list_of_symbols.append(x.symbol)
                    x.saving_data_files()
                    x.killObj()
                    print('  Object Deleted!')
                print(list_of_symbols)
        return list_of_symbols