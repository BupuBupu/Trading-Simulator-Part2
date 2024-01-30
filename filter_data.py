import numpy as np
import pandas as pd
from datetime import date
from jugaad_data.nse import stock_df

# store data for last 1 week
def save_df(symbol):
    """
        Inputs:
        symbol--->Stock type which needs to be converted to DataFrame
        last_year--->Stores stock data for the past last {last_years} years
        
        Outputs:
        returns a DataFrame comprising Data accordingly in float32(DownCasted from float64)
    """
    today = date.today()
    df=""
    if(today.day-7<1 and today.month-1>=1):
        df=stock_df(symbol=symbol, from_date=date(today.year, today.month-1, 21), to_date=today, series="EQ")
    elif(today.day-7<1 and today.month-1>=1):
        df=stock_df(symbol=symbol, from_date=date(today.year-1, 12, 23), to_date=today, series="EQ")
    else:
        df = stock_df(symbol=symbol, from_date=date(today.year, today.month, today.day-7), to_date=today, series="EQ")
    
    # Removing unnecessary data to optimize storing and loading process
    to_remove=["SERIES", "PREV. CLOSE", "VWAP", "52W H", "52W L", "SYMBOL"]
    #print(df)
    for col in to_remove:
        df.drop(labels=col, axis=1, inplace=True)
    # Downcasting float64 to float32 in all columns to save some memory
    df=pd.concat([df["DATE"], df[df.columns[1:]].astype("float32", copy=True)], axis=1)
    return df

def filtered_data(stocks):
    # Will store df of last 1 week for every stock
    dfs = []
    for i in range(len(stocks)):
        df = save_df(stocks[i])
        new_df = df["DATE"]
        
        new_df["DAILY INCREMENT"]=((df["CLOSE"]-df["OPEN"])/df["CLOSE"])*100
        new_df["AVERAGE"]=(df["CLOSE"]+df["OPEN"])/2
        new_df["TRADES PER VOLUME"]=df["NO OF TRADES"]/df["VOLUME"]
        dfs.append(new_df)
    
    daily_inc = [[dfs[i]["DAILY INCREMENT"].iloc[0], stocks[i]] for i in range(len(stocks))]
    average = [[dfs[i]["AVERAGE"].iloc[0], stocks[i]] for i in range(len(stocks))]
    trades_per_vol = [[dfs[i]["TRADES PER VOLUME"].iloc[0], stocks[i]] for i in range(len(stocks))]
    
    params=[daily_inc, average, trades_per_vol]
    for i in range(3):
        params[i].sort(reverse=True)
    return params
