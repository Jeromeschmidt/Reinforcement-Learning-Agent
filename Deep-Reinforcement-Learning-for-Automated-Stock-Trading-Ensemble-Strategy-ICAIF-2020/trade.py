# common library
import pandas as pd
import numpy as np
import time
from stable_baselines.common.vec_env import DummyVecEnv

# preprocessor
from preprocessing.preprocessors import *
from preprocessing.alpaca_api import *
# config
from config.config import *
# model
from model.models import *
import os


from run_DRL import run_model
import alpaca_trade_api as alpaca



def load_model(tickers):
    '''Load in the pretrained model from the trained models folder '''
    try:
        model = run_model(tickers)
    except:
        # get model from trained model files
        pass

    return model


def makeTrades():
    ''' predicts on current state '''

    action, _states = model.predict(df)

    actions = actions * HMAX_NORMALIZE
    #actions = (actions.astype(int))
    # if self.turbulence>=self.turbulence_threshold:
    #     actions=np.array([-HMAX_NORMALIZE]*STOCK_DIM)

    begin_total_asset = self.state[0]+ \
    sum(np.array(self.state[1:(STOCK_DIM+1)])*np.array(self.state[(STOCK_DIM+1):(STOCK_DIM*2+1)]))
    #print("begin_total_asset:{}".format(begin_total_asset))

    argsort_actions = np.argsort(actions)

    sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
    buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]

    for index in sell_index:
        # print('take sell action.format(actions[index]))
        self._sell_stock(index, actions[index])

    for index in buy_index:
        # print('take buy action: {}'.format(actions[index]))
        self._buy_stock(index, actions[index])

if __name__ == "__main__":
    model = load_model()

    isOpen = self.alpaca.get_clock().is_open
    while(not isOpen):
        clock = self.alpaca.get_clock()
        openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
        timeToOpen = int((openingTime - currTime) / 60)
        print(str(timeToOpen) + " minutes til market open.")
        time.sleep(60)
        isOpen = self.alpaca.get_clock().is_open

    makeTrades(model)
