# common library
import pandas as pd
import numpy as np
import time
from stable_baselines.common.vec_env import DummyVecEnv

# preprocessor
from preprocessing.preprocessors import *
from preprocessing.alpaca_api import *
from preprocessing.GetStocks import *
# config
from config.config import *
# model
from model.models import *
import os
from stable_baselines import A2C

from run_DRL import run_model


account = api.get_account()

HMAX_NORMALIZE = 100
STOCK_DIM = 20


def load_model(tickers):
    '''Load in the pretrained model from the trained models folder '''
    # model = run_model(tickers)

    # try:
    #     model = run_model(tickers)
    # except:
    #     # get model from trained model files to find most recent trained model
    #     pass

    model = A2C.load("trained_models/2021-03-22 18:25:09.528982/A2C_30k_dow_120.zip")

    return model


def makeTrades(df, model):
    '''predicts on current state using pretrained model'''
    mappings = dict()
    i = 0

    for index, row in df.iterrows():
        mappings[i] = row['tic']
        i += 1

    print(mappings)

    data = [account.buying_power] + \
                  df.adjcp.values.tolist() + \
                  [0]*STOCK_DIM + \
                  df.macd.values.tolist() + \
                  df.rsi.values.tolist() + \
                  df.cci.values.tolist() + \
                  df.adx.values.tolist()


    actions, _states = model.predict(data)

    actions = actions * HMAX_NORMALIZE
    print(actions)

    argsort_actions = np.argsort(actions)

    sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
    buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]

    portfolio = api.list_positions()

    for index in sell_index:
        print('take sell action {}'.format(mappings[index]))
        api.submit_order(symbol=mappings[index],qty=abs(int(actions[index])),side='sell',type='market',time_in_force='day')

    for index in buy_index:
        print('take buy action: {}'.format(actions[index]))
        api.submit_order(symbol=mappings[index],qty=int(actions[index]),side='buy',type='market',time_in_force='day')



if __name__ == "__main__":
    # tickers = get_highest_movers()
    tickers = ['AMCR', 'CCL', 'ETSY', 'OXY', 'NCLH', 'FLS', 'SIVB', 'V', 'FANG', 'DG', 'MCHP', 'ENPH', 'MRO', 'BBY', 'CB', 'APA', 'DISCK', 'XRX', 'NKE', 'DISCA']
    print(tickers)

    model = load_model(tickers)

    # isOpen = self.alpaca.get_clock().is_open
    # while(not isOpen):
    #     clock = self.alpaca.get_clock()
    #     openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
    #     currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
    #     timeToOpen = int((openingTime - currTime) / 60)
    #     print(str(timeToOpen) + " minutes til market open.")
    #     time.sleep(60)
    #     isOpen = self.alpaca.get_clock().is_open

    # Get previous day stock information from alpaca as df
    data = preprocess_data(tickers, limit=2)
    data = data[(data.datadate >= data.datadate.max())]
    data = data.reset_index()
    data = data.drop(["index"], axis=1)
    data = data.fillna(method='ffill')
    print(data)

    #make trades on current stock data 
    makeTrades(data, model)
