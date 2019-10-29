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
import  moduleNews
import moduleRun as run
from moduleRun import connect
register_matplotlib_converters()
pd.set_option('max_columns',None)

class PythonDB:
    connection = None
    cursor = None

    def __init__(self):
        try:
            PythonDB.connection = pymysql.connect('127.0.0.1','root','', 'test') # servername or ip/ username/ password/ databasename
            PythonDB.cursor = PythonDB.connection.cursor() #cursor is used to execute the database commands
        except Exception as e:
            print(e.args)
        else:
            print("Connection established successfully")

    def insertTrade(self, listi):
        try:
            command = '''INSERT INTO algo_m1 (date,tradeId,buysell,symbol) VALUES(%s,%s,%s,%s)'''
            PythonDB.cursor.executemany(command, listi)
        except Exception as e:
           print(e.args)
        else:
            PythonDB.connection.commit()  # save changes in the table content
            print("Record inserted succesfully")

    def insert_news(self,listi):
        try:
            command = '''INSERT INTO news (date,tradeId,buysell,symbol,action) VALUES(%s,%s,%s,%s,%s)'''
            PythonDB.cursor.executemany(command, listi)
        except Exception as e:
           print(e.args)
        else:
            PythonDB.connection.commit()  # save changes in the table content
            print("Record inserted succesfully")


    def listdata(self, tablename):
        data=None
        try:
            command = '''SELECT * FROM %s''' %(tablename)
            PythonDB.cursor.execute(command)
        except Exception as e:
            print(e.args)
        else:
            data = PythonDB.cursor.fetchall()
        return data

    def delTrade(self,tablename,tradeId):
        command = '''DELETE FROM %s WHERE tradeId = %d'''%(tablename,tradeId)
        PythonDB.cursor.execute(command)
        PythonDB.connection.commit()
        print('Trade deleted succesfuly!')

    def delSymbol(self,tablename,symbol):
        command = '''DELETE FROM %s WHERE symbol = "%s" ''' %(tablename, symbol)
        PythonDB.cursor.execute(command)
        PythonDB.connection.commit()
        print('Symbol deleted succesfuly!')

#Functions out of the Classes

def openedSupRes():
    openedSupport={}
    openedResistance={}
    info = con.get_open_positions(kind=list)
    for x in range(len(info)):
        if info.iloc[x]['amountK']==12 and info.iloc[x]['isBuy']==True:
            openedSupport[info.iloc[x]['currency']]=info.iloc[x]['tradeId']
        if info.iloc[x]['amountK']==12 and info.iloc[x]['isBuy']==False:
            openedResistance[info.iloc[x]['currency']]=info.iloc[x]['tradeId']
    return openedSupport,openedResistance

def openedCurrency():
    global opened_possitions_list
    opened_possitions_list = []
    info = con.get_open_positions(kind=list)
    num = len(info)
    if num != 0:
        for x in range(0, num):
            opened_possitions_list.append(info.iloc[x]['currency'])
    print(opened_possitions_list)
    return opened_possitions_list

def primarySupRes(x,xBuy,xSell,xOrders):
    x.sup, x.res, x.supList, x.resList, x.newdata,x.maxima,x.minima = x.supres5()
    minima=x.minima
    maxima=x.maxima
    print(x.sup, x.res, x.supList, x.resList,x.maxima,x.minima)
    if (xSell and x.sup == None) or (xBuy and x.res == None):
        print('   secondary   check')
        x.sup, x.res,x.maxima,x.minima = x.supres2(x.newdata)
    if (xSell and x.sup != None) :
        x.stop = False
        if len(x.supList)>=2:
            xOrders=x.supportEntry(x.supList,minima)
    if (xBuy and x.res != None):
        x.stop = False
        if len(x.resList)>=2:
            xOrders=x.resistanceEntry(x.resList,maxima)
    return x.stop,xOrders

def orders_list():
    orders_symbol_list=[]
    list_of_orders = con.get_orders(kind='list')
    for x in list_of_orders:
        orders_symbol_list.append(x['currency'])
    return list_of_orders,orders_symbol_list

def deleting_news_from_database(symbol,list_of_orders):
    symbols_list=[]
    for x in list_of_orders:
        symbols_list.append(x['currency'])
    if symbol not in symbols_list:
        DB.delSymbol('news',symbol)

def delete_orders(symbol,list_of_orders):
    Orders=False
    count=0
    for x in list_of_orders:
        if x['currency']==symbol:
            count+=1
    if count % 2 !=0:
        for x in list_of_orders:
            if x['currency']==symbol:
                con.delete_order(x['orderId'])
    if count >=1:
        Orders=True
    return Orders

def Correlated_List_Descision(Trues_List_1):
    if False in Trues_List_1:
        corelated1Bolean=False
    else:
        corelated1Bolean=True
    return corelated1Bolean

def Correlated_List_Descision2(Trues_List_2):
    if False in Trues_List_2:
        corelated2Bolean=False
    else:
        corelated2Bolean=True
    return corelated2Bolean

def Correlated_List_Descision3(Trues_List_3):
    if False in Trues_List_3:
        corelated3Bolean=False
    else:
        corelated3Bolean=True
    return corelated3Bolean

def trues_list_refresh(x,x_stop):
    if x in correlated_List_1:
        Trues_List_1.append(x_stop)
    if x in correlated_List_2:
        Trues_List_2.append(x_stop)
    if x in correlated_List_3:
        Trues_List_3.append(x_stop)

def Database_Info_algo_m1():
    symbols=[]
    tuple_of_orders_in_DB = DB.listdata('algo_m1')
    for x in tuple_of_orders_in_DB:
        symbols.append(x[-1])
    return  symbols,tuple_of_orders_in_DB

def Database_Info_news():
    symbols=[]
    tuple_of_orders_in_DB = DB.listdata('news')
    for x in tuple_of_orders_in_DB:
        symbols.append(x[-1])
    return  symbols,tuple_of_orders_in_DB

def get_offers():
    offer=con.get_offers(kind='dataframe')
    return offer

def set_all_in_correlated_list_1(x):
    print(Trues_List_1)
    global corelated1Bolean
    if x in correlated_List_1:
        if corelated1Bolean == True:
            corelated1Bolean=Correlated_List_Descision(Trues_List_1)
        if corelated1Bolean==False:
            for x in correlated_List_1:
                x.stop=False
        print('Correlated Bolean 1===   '+str(corelated1Bolean))

def set_all_in_correlated_list_2(x):
    print(Trues_List_2)
    global corelated2Bolean
    if x in correlated_List_2:
        if corelated2Bolean == True:
            corelated2Bolean=Correlated_List_Descision2(Trues_List_2)
        if corelated2Bolean==False:
            for x in correlated_List_2:
                x.stop=False
        print('Correlated Bolean 2===   '+str(corelated2Bolean))

def set_all_in_correlated_list_3(x):
    print(Trues_List_3)
    global corelated3Bolean
    if x in correlated_List_3:
        if corelated3Bolean == True:
            corelated3Bolean = Correlated_List_Descision2( Trues_List_3)
        if corelated3Bolean == False:
            for x in correlated_List_3:
                x.stop = False
        print('Correlated Bolean 3===   ' + str(corelated3Bolean))

def MainLoad():
    global symbols,corelated1Bolean,corelated2Bolean,corelated3Bolean,correlated_List_1,correlated_List_2,correlated_List_3,\
        Trues_List_1,Trues_List_2,Trues_List_3

    p1=run.Run('AUD/JPY')
    p2=run.Run('GBP/JPY')
    p3=run.Run('USD/JPY')
    p4=run.Run('EUR/JPY')
    p22=run.Run('CAD/JPY')
    p9=run.Run('CHF/JPY')

    p5=run.Run('NZD/USD')
    p6=run.Run('NZD/CHF')
    p7=run.Run('AUD/USD')
    p8=run.Run('AUD/CAD')

    p10=run.Run('USD/CHF')
    p11=run.Run('GBP/AUD')
    p12=run.Run('GBP/CAD')
    p13=run.Run('AUD/NZD')
    p14=run.Run('EUR/USD')
    p15=run.Run('GBP/USD')
    p16=run.Run('EUR/GBP')
    p17=run.Run('GBP/CHF')
    p18=run.Run('USD/CAD')
    ########################
    p20=run.Run('EUR/CAD')
    p21=run.Run('EUR/CHF')
    symbols=[p1,p22,p3,p4,p5,p6,p7,p8,p11,p12,p15,p17,p2]
    #symbols=[p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14,p15,p16,p17,p18,p20,p21,p22]
    correlated_List_1 = [p1,p22,p3,p4]
    correlated_List_2 =[p5,p6,p7,p8]
    correlated_List_3 =[p11,p12,p15,p17,p2]
    corelated1Bolean=True
    corelated2Bolean=True
    corelated3Bolean=True
    Trues_List_1=[]
    Trues_List_2 = []
    Trues_List_3 = []

    list_with_opened_possitions_at_marker=openedCurrency()
    symbols_in_DB, tuple_of_orders_in_DB = Database_Info_algo_m1()
    for z in symbols_in_DB:
        if z not in list_with_opened_possitions_at_marker:
            DB.delSymbol('algo_m1', z)
    print(symbols_in_DB)
    for x in symbols:
        x.readyH1b, x.readyH1s =False,False
        x.ready30b,x.ready30s = False,False
        x.ready15b, x.ready15s=False,False
        x.ready5b, x.ready5s = False,False
        x.ready1b, x.ready1s = False,False
        x.dataH4()

        x.dataH1()
        x.data30()
        x.data15()
        x.data5()
        x.data1()
        x.Buy,x.Sell,x.readyH1b,x.readyH1s=x.AlgoH4()
        x.stop = True
        x.stop,x.Orders = primarySupRes(x,x.Buy,x.Sell,None)
        trues_list_refresh(x,x.stop)
        print('x.Stop:     '+str(x.stop))
        print('x.Orders:   '+str(x.Orders))
    list_of_orders,orders_symbol_list=orders_list()
    for x in symbols:
        x.Orders=delete_orders(x.symbol,list_of_orders)
        print(x.symbol)
        print('x.Orders:   ' + str(x.Orders))

        set_all_in_correlated_list_1(x)
        set_all_in_correlated_list_2(x)
        set_all_in_correlated_list_3(x)

    for x in symbols:
        if x.stop:
            count=x.count(60)
            x.ready30b,x.ready30s=x.AlgoH1(x.readyH1b,x.readyH1s,count)
            count=x.count(30)
            x.ready15b,x.ready15s = x.Algom30(x.ready30b,x.ready30s,count)
            count=x.count(15)
            x.ready5b,x.ready5s = x.Algom15(x.ready15b,x.ready15s,count)
            x.ready1b,x.ready1s = x.Algom5(x.ready5b,x.ready5s)
            x.Algo_m1_ema10(x.ready1b,x.ready1s)
        if x.readyH1b :
            print('Buy ready 1H')
        if x.readyH1s:
            print('Sell ready 1H')
        if x.ready30b :
            print('Buy ready 30')
        if x.ready30s:
            print('Sell ready 30')
        if x.ready15b :
            print('Buy ready 15')
        if x.ready15s:
            print('Sell ready 15')
        if x.ready5b :
            print('Buy ready 5')
        if x.ready5s:
            print('Sell ready 5')
        if x.ready1b :
            print('Buy ready 1')
        if x.ready1s:
            print('Sell ready 1')
        print(x.symbol + ' loaded')
        print('x.stop :  '+str(x.stop))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    for x in correlated_List_1:
        print(str(x.stop)+'   '+str(x.symbol))
    for x in correlated_List_2:
        print(str(x.stop) + '   ' + str(x.symbol))
    for x in correlated_List_3:
        print(str(x.stop) + '   ' + str(x.symbol))
    print('done')
    print('running...')

def four_hour_ckeck():
    currenttime = dt.datetime.now()
    print(currenttime)
    for x in symbols:
        x.killH4()
        x.dataH4()
        x.Buy, x.Sell, x.readyH1b, x.readyH1s = x.AlgoH4()
        print(x.symbol)
        print('................')
    print('H4 Checked')
def one_hour_check():
    for x in symbols:
        if x.readyH1b or x.readyH1s and x.stop:
            x.killH1()
            x.dataH1()
            count = x.count(60)
            x.ready30b, x.ready30s = x.AlgoH1(x.readyH1b, x.readyH1s, count)
            if x.readyH1b:
                print('H1  Ready  BUY')
            if x.readyH1s:
                print('H1  Ready  SELL')
            print(x.symbol)
            print('................')
    print('H1 Checked')
    print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-')
def min_30_check():
    opened = openedCurrency()
    offer = get_offers()
    print('Checking   30M....')
    for x in symbols:
        x.pas = True
        if x.ready30b or x.ready30s and x.stop:
            x.pas = False
            x.kill30()
            x.data30()
            count = x.count(30)
            x.ready15b, x.ready15s = x.Algom30(x.ready30b, x.ready30s, count)
            print(x.symbol)
            if x.ready30b:
                print('M30  Ready    BUY')
            if x.ready30s:
                print('M30  Ready    SELL')
        if x.pas:
            x.kill30()
            x.data30()
        print('................')
    print('M30 CHECKED!')
    print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
def min_15_check():
    global opened
    print('Checking  15M....')
    opened = openedCurrency()
    for x in symbols:
        if (x.ready30b and x.ready15b) or (x.ready30s and x.ready15s) and x.stop:
            x.kill15()
            x.data15()
            count = x.count(15)
            x.ready5b, x.ready5s = x.Algom15(x.ready15b, x.ready15s, count)
            if x.ready15b:
                print('M15  Ready    BUY')
            if x.ready15s:
                print('M15  Ready    SELL')
            print(x.symbol)
            print('................')
    print('M15 CHECKED!')
    print('-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_')
def min_5_check():
    global Trues_List_1,Trues_List_2,Trues_List_3
    list_of_orders, orders_symbol_list = orders_list()
    Trues_List_1 = []
    Trues_List_2 = []
    Trues_List_3 = []
    for x in symbols:
        if x.symbol in orders_symbol_list:
            x.Orders = True

    for x in symbols:
        if x.readyH1b or x.readyH1s:
            x.kill5()
            x.data5()
            x.stop, x.Orders = primarySupRes(x, x.Buy, x.Sell, x.Orders)
            trues_list_refresh(x, x.stop)
            set_all_in_correlated_list_1(x)
            set_all_in_correlated_list_2(x)
            set_all_in_correlated_list_3(x)
            print('x.stop:                                                                     ' + str(x.stop))
    for x in symbols:
        symbol = x.symbol
        if (x.ready30b and x.ready15b and x.ready5b) or (x.ready30s and x.ready15s and x.ready5s) and x.stop:
            if x.symbol in opened:
                opened = openedCurrency()
            if symbol not in opened:
                x.ready1b, x.ready1s = x.Algom5(x.ready5b, x.ready5s)
                if x.ready5b:
                    print('M5  Ready    BUY')
                if x.ready5s:
                    print('M5  Ready    SELL')
            print(x.symbol)
            print('................')
    print('M5 CHECKED')
def min_1_check():
    currenttime = dt.datetime.now()
    for x in symbols:
        symbol = x.symbol
        if x.Orders == True:
            list_of_orders, orders_symbol_list = orders_list()
            x.Orders = delete_orders(x.symbol, list_of_orders)
        if (x.ready30b and x.ready15b and x.ready5b and x.ready1b) or (
                x.ready30s and x.ready15s and x.ready5s and x.ready1s) and x.stop:
            symbols_in_DB, tuple_of_orders_in_DB = Database_Info_algo_m1()
            if symbol in symbols_in_DB:
                opened = openedCurrency()
                for z in symbols_in_DB:
                    if z not in opened:
                        DB.delSymbol('algo_m1', z)
                if tuple_of_orders_in_DB[-2] == 'BUY':
                    isBuy = True
                else:
                    isBuy = False
                x.close_m1(isBuy, tuple_of_orders_in_DB[-3])
            if symbol not in symbols_in_DB:
                x.kill1()
                x.data1()
                x.Algo_m1_ema10(x.ready1b, x.ready1s)
            if x.ready1b:
                print('M1  Ready    BUY')
            if x.ready1s:
                print('M1  Ready    SELL')
            print(x.symbol)
            print('................')
    print(currenttime)
    print('------------------------')

def MainWhile():
    global Trues_List_1,Trues_List_2,Trues_List_3
    while True:
        currenttime = dt.datetime.now()
        list_of_symbols=moduleNews.NewsAction()
        if len(list_of_symbols)!=0:
            print('list_of symbols !=0')
            for x in symbols:
                if x.symbol in list_of_symbols:
                    x.Orders=True
            list_of_symbols=[]
        if currenttime.second==10 :
            if (currenttime.hour+1) % 4==0 and currenttime.minute==0:
                four_hour_ckeck()
            if currenttime.minute==0:
                one_hour_check()
            if currenttime.minute % 30==0:
                min_30_check()
            if currenttime.minute % 15==0:
                min_15_check()
            if currenttime.minute % 5 == 0:
                min_5_check()
        min_1_check()
        time.sleep(1)

con=run.connect()
DB=PythonDB()
MainLoad()
MainWhile()
while True:
    try:
        connect()
        DB = PythonDB()
        MainLoad()
        MainWhile()
    except Exception as e:
        print(e)
        time.sleep(120)
