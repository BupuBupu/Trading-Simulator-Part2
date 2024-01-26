import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import numpy as np
from jugaad_data.nse import stock_df

def save_df(symbol, last_years):
    """
        Inputs:
        symbol--->Stock type which needs to be converted to DataFrame
        last_year--->Stores stock data for the past last {last_years} years
        
        Outputs:
        returns a DataFrame comprising Data accordingly in float32(DownCasted from float64)
    """
    today = date.today()
    df = stock_df(symbol=symbol, from_date=date(today.year-last_years, today.month, today.day), to_date=today, series="EQ")
    # Removing unnecessary data to optimize storing and loading process
    to_remove=["SERIES", "PREV. CLOSE", "VWAP", "52W H", "52W L", "SYMBOL"]
    #print(df)
    for col in to_remove:
        df.drop(labels=col, axis=1, inplace=True)
    # Downcasting float64 to float32 in all columns to save some memory
    df=pd.concat([df["DATE"], df[df.columns[1:]].astype("float32", copy=True)], axis=1)
    return df

def store_stocks(symbols, years):
    # respective store dfs of respective symbols and years, where symbols and years are a list\
    if(len(symbols)==0):
        return pd.DataFrame()
    stocksDF=[]
    length = len(symbols)
    for i in range(length):
        df = save_df(symbols[i], years[i])
        print("i:", i)
        df = pd.DataFrame({
            symbols[i]:df["CLOSE"].to_numpy()
        }, index=df["DATE"])
        stocksDF.append(df)
    # Merging all based on close prices based on index i.e. DATE
    df_merged=stocksDF[0]
    for i in range(1, length):
        df_merged = df_merged.merge(stocksDF[i], left_index=True, right_index=True)
        
    return df_merged
        
def plot_to_html(df_merged):
    if(df_merged.empty):
        go.Figure().show()
        return
    dfmon_merged = df_merged.resample('M').last()
    dfyr_merged = df_merged.resample('AS').last()
    
    df_merged.index.names = ['Date']
    df_merged.reset_index(inplace=True)
    
    dfmon_merged.index.names = ['Date']
    dfmon_merged.reset_index(inplace=True)
    
    dfyr_merged.index.names = ['Date']
    dfyr_merged.reset_index(inplace=True)
    
    fig = go.Figure()
    dfs = {'daily':df_merged, 'monthly': dfmon_merged, 'yearly' :dfyr_merged}
    
    # specify visibility for traces accross dataframes
    frames = len(dfs) # number of dataframes organized in  dict
    columns = len(dfs['daily'].columns) - 1 # number of columns i df, minus 1 for Date
    scenarios = [list(s) for s in [e==1 for e in np.eye(frames)]]
    visibility = [list(np.repeat(e, columns)) for e in scenarios] 
    
    # container for buttons
    buttons = []

    # iterate of dataframes in dfs:
    # - i is used to reference visibility attributes
    # - k is the name for each dataframe
    # - v is the dataframe itself
    for i, (k, v) in enumerate(dfs.items()):
        print(i)
        for c, column in enumerate(v.columns[1:]):
            fig.add_scatter(name = column,
                            x = v['Date'],
                            y = v[column], 
                            visible=True if k=='daily' else False # 'daily' values are shown from the   start
                           )
                
        # one button per dataframe to trigger the visibility
        # of all columns / traces for each dataframe
        button =  dict(label=k,
                       method = 'restyle',
                       args = ['visible',visibility[i]])
        buttons.append(button)

    # include dropdown updatemenu in layout
    fig.update_layout(updatemenus=[dict(type="dropdown",
                                        direction="down",
                                        buttons = buttons)])
    fig.update_layout(
        dragmode="zoom",
        hovermode="x",
        legend=dict(traceorder="reversed"),
        height=800,
        template="plotly_white",
        margin=dict(
            t=100,
            b=100
        ),
    )
    my_script = pio.to_html(fig, full_html=False)
    return my_script
# df = store_stocks([], [])
# plot_to_html(df)