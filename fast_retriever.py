import base64
import json

from bytewax.dataflow import Dataflow
import bytewax
#sfrom websocket import create_connection
import websocket

# input
ticker_list = ["AMZN", "MSFT"]

def yf_input(worker_tickers, state):
    ws = websocket.create_connection("wss://streamer.finance.yahoo.com/")
    ws.send(json.dumps({"subscribe":worker_tickers}))
    while True:
        yield state, ws.recv()

def input_builder(worker_index, worker_count, resume_state):
    state = resume_state or None
    worker_tickers = list(bytewax.inputs.distribute(ticker_list, worker_index, worker_count))
    print({"subscribing to": worker_tickers})
    return yf_input(worker_tickers, state)

flow = Dataflow("8ji9aj")
flow.input("input", bytewax.inputs.ManualInputConfig(input_builder))