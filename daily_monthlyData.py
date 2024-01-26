import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import numpy as np
from jugaad_data.nse import stock_df

symbol = "SBIN"
years=5
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

df1=save_df(symbol, years)
df2=save_df("BHARTIARTL", 5)
# print("DF1:")
# print(df1["CLOSE"])
# print(df1["DATE"])
# print("DF2:")
# print(df2["CLOSE"])
# print(df2["DATE"])
df=pd.DataFrame({
    symbol:df1["CLOSE"].to_numpy(),
}, index=df1["DATE"])
df_=pd.DataFrame({
    "BHARTIARTL":df2["CLOSE"].to_numpy()
}, index=df2["DATE"])
df = pd.merge(df, df_, left_index=True, right_index=True) # inner join, i.e. intersection of indices
# print(df.head())
# print("----------------")
#df.set_index("DATE", inplace=True)

# print(df.head())
# print("----------------")
dfmon = df.resample('M').last()
# print(dfmon.head())
# print("----------------")
dfyr = df.resample('AS').last()
# print(dfyr.head())
# print("----------------")

df.index.names = ['Date']
df.reset_index(inplace= True)

dfmon.index.names = ['Date']
dfmon.reset_index(inplace= True)

dfyr.index.names = ['Date']
dfyr.reset_index(inplace= True)
# print(dfyr.head())
fig = go.Figure()
dfs = {'daily':df, 'monthly': dfmon, 'yearly' :dfyr}

# # your setup this far...

# # ... here is where I've added my contributions:

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
                        visible=True if k=='daily' else False # 'daily' values are shown from the start
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
fig.show()