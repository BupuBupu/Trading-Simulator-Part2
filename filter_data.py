import numpy as np
import warnings
import pandas as pd
from datetime import date
from jugaad_data.nse import stock_df
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.io as pio

warnings.simplefilter(action='ignore', category=FutureWarning)
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
    for col in to_remove:
        df.drop(labels=col, axis=1, inplace=True)
    df=pd.concat([df["DATE"], df[df.columns[1:]].astype("float", copy=True)], axis=1)
    return df

def filtered_data():
    '''
    Returns a 3d list, first indexes are based on the params and each params has 2d list which is a vector of pairs, where the first value represents the param value and second value represents the corresponding Stock name.
    '''
    # Will store df of last 1 week for every stock
    stocks = ['ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LTIM', 'LT', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'UPL', 'ULTRACEMCO', 'WIPRO']
    dfs = []
    for i in range(len(stocks)):
        df = save_df(stocks[i])
        new_df = df["DATE"]
        new_df["OPEN"] = df["OPEN"]
        new_df["CLOSE"] = df["CLOSE"]
        new_df["DAILY INCREMENT"]=((df["CLOSE"]-df["OPEN"])/df["CLOSE"])*100
        new_df["AVERAGE"]=(df["CLOSE"]+df["OPEN"])/2
        new_df["TRADES PER VOLUME"]=df["NO OF TRADES"]/df["VOLUME"]
        dfs.append(new_df)

    open_pr = [[dfs[i]["OPEN"].iloc[0], stocks[i]] for i in range(len(stocks))]
    close_pr = [[dfs[i]["CLOSE"].iloc[0], stocks[i]] for i in range(len(stocks))]
    daily_inc = [[dfs[i]["DAILY INCREMENT"].iloc[0], stocks[i]] for i in range(len(stocks))]
    average = [[dfs[i]["AVERAGE"].iloc[0], stocks[i]] for i in range(len(stocks))]
    trades_per_vol = [[dfs[i]["TRADES PER VOLUME"].iloc[0], stocks[i]] for i in range(len(stocks))]
    
    params={"open_pr":open_pr, "close_pr":close_pr, "daily_inc":daily_inc, "average":average, "trades_per_vol":trades_per_vol}
    return params

def table_const(params):
    # Construct table based on the parameters for further use
    stocks = ['ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LTIM', 'LT', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'UPL', 'ULTRACEMCO', 'WIPRO']
    # params is a dictionary now
    my_data = pd.DataFrame({"Rank":np.arange(1, len(stocks)+1), "Stocks":stocks})
    
    open_pr = []
    for i in range(len(stocks)):
        open_pr.append(params["open_pr"][i][0])
    close_pr = []
    for i in range(len(stocks)):
        close_pr.append(params["close_pr"][i][0])
    daily_inc = []
    for i in range(len(stocks)):
        daily_inc.append(params["daily_inc"][i][0])
    average=[]
    for i in range(len(stocks)):
        average.append(params["average"][i][0])
    trades_per_vol=[]
    for i in range(len(stocks)):
        trades_per_vol.append(params["trades_per_vol"][i][0])
    
    my_data["open"]=open_pr
    my_data["close"]=close_pr
    my_data["daily_inc"]=daily_inc
    my_data["average"]=average
    my_data["trades_per_vol"]=trades_per_vol
    my_data = my_data.round(4)
    return my_data

    
def table_to_html(my_data, sort_based_on):
    my_data.sort_values(by=[sort_based_on], ascending=False, inplace=True)
    my_data.reset_index(inplace=True, drop=True)
    my_data["Rank"]=my_data.index+1
    my_data.rename(columns={sort_based_on:sort_based_on+"\u2193"}, inplace=True)
    
    header = my_data.columns.tolist()
    values = my_data.transpose().values.tolist()
    print(header)
    col_to_color = header.index(sort_based_on+"\u2193")
    color='#FFD700'
    others='#FFFFCC'
    colors = [others]*len(header)
    colors[col_to_color]=color

    fig = go.Figure(
        data=[
            go.Table(header=dict(values=header),
            cells=dict(values=values, fill_color=colors)
            )
        ]
    )
    my_script = pio.to_html(fig, full_html=False)
    return my_script
