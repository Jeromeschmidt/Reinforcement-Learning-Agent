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


from run_DRL import run_model
import alpaca_trade_api as alpaca



def load_model(tickers):
    '''Load in the pretrained model from the trained models folder '''
    model = None
    try:
        model = run_model(tickers)
    except:
        # get model from trained model files to find most recent trained model
        pass

    return model


def makeTrades(df, model, tickers):
    '''predicts on current state using pretrained model'''


    # action, _states = model.predict(df)
    #
    # actions = actions * HMAX_NORMALIZE
    # #actions = (actions.astype(int))
    # # if self.turbulence>=self.turbulence_threshold:
    # #     actions=np.array([-HMAX_NORMALIZE]*STOCK_DIM)
    #
    # begin_total_asset = self.state[0]+ \
    # sum(np.array(self.state[1:(STOCK_DIM+1)])*np.array(self.state[(STOCK_DIM+1):(STOCK_DIM*2+1)]))
    # #print("begin_total_asset:{}".format(begin_total_asset))
    #
    # argsort_actions = np.argsort(actions)
    #
    # sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
    # buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]
    #
    # for index in sell_index:
    #     # print('take sell action.format(actions[index]))
    #     self._sell_stock(index, actions[index])
    #     [0,1,-1]
    #     self stock at in df at index index for the quanitiy of actions[index]
    #
    # for index in buy_index:
    #     # print('take buy action: {}'.format(actions[index]))
    #     self._buy_stock(index, actions[index])
    pass


def prediction(df):
    ''' predicts on current state '''
    
    model = loads_model()
    
    action, _states = model.predict(df)
    
    obs_trade, rewards, dones, info = env_trade.step(action)

       


if __name__ == "__main__":
    # tickers = get_highest_movers()
    tickers = ['AMCR', 'CCL', 'ETSY', 'OXY', 'NCLH', 'FLS', 'SIVB', 'V', 'FANG', 'DG', 'MCHP', 'ENPH', 'MRO', 'BBY', 'CB', 'APA', 'DISCK', 'XRX', 'NKE', 'DISCA']

    # model = load_model(tickers)

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
    print(data)


    # makeTrades(df, model, tickers)
