# common library
import pandas as pd
import numpy as np
import time
import gym
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
# custom env 
from env.EnvMultipleStock_trade import StockEnvTrade

account = api.get_account()

INITIAL_ACCOUNT_BALANCE=100000
HMAX_NORMALIZE = 100
STOCK_DIM = 20
TRANSACTION_FEE_PERCENT = 0.001
asset_memory = [INITIAL_ACCOUNT_BALANCE]
cost = 0
trades = 0
reward = 0
rewards_memory = []
day = 0
REWARD_SCALING = 1e-4


tickers = ['AMCR', 'CCL', 'ETSY', 'OXY', 'NCLH', 'FLS', 'SIVB', 'V', 'FANG', 'DG', 'MCHP', 'ENPH', 'MRO', 'BBY', 'CB', 'APA', 'DISCK', 'XRX', 'NKE', 'DISCA']
data = preprocess_data(tickers, limit=2)
data = data[(data.datadate >= data.datadate.max())]
data = data.reset_index()
data = data.drop(["index"], axis=1)
data = data.fillna(method='ffill')

# print((data.cci.values).tolist())
# print(type((data.cci.values).tolist()))

# for num in data.cci.values.tolist():
    
#     print(type(int(num)))

# state = [int(account.buying_power)] + \
#         data.adjcp.values.tolist() + \
#         [0]*STOCK_DIM + \
#         int(float(data.macd.values.tolist())) + \
#         int(float(data.rsi.values.tolist())) + \
#         int(float(data.cci.values)) + \
#         data.adx.values.tolist()
        
        
state = [INITIAL_ACCOUNT_BALANCE] + \
                data.adjcp.values.tolist() + \
                [0]*STOCK_DIM + \
                data.macd.values.tolist() + \
                data.rsi.values.tolist() + \
                data.cci.values.tolist() + \
                data.adx.values.tolist()
                
def info(cost=0, trades=0):
    cost += cost
    trades += trades
    return 
    

def load_model(tickers):
    '''Load in the pretrained model from the trained models folder '''
    # model = run_model(tickers)

    # try:
    #     model = run_model(tickers)
    # except:
    #     # get model from trained model files to find most recent trained model
    #     pass
    #loads pretrained model
    model = A2C.load("trained_models/2021-03-22 18:25:09.528982/A2C_30k_dow_120.zip")

    return model

def map_stocks_index(df):
    '''maps df to index to correct ticker '''
    mappings = dict()
    i = 0

    for index, row in df.iterrows():
        mappings[i] = row['tic']
        i += 1
    
    return mappings

def render(mode='human',close=False):
    '''returns state'''
    return state

def buy_stock(index, action, mappings):
    # state = [account.buying_power] + \
    #               df.adjcp.values.tolist() + \
    #               [0]*STOCK_DIM + \
    #               df.macd.values.tolist() + \
    #               df.rsi.values.tolist() + \
    #               df.cci.values.tolist() + \
    #               df.adx.values.tolist()
    # perform buy action based on the sign of the action
    # if self.turbulence< self.turbulence_threshold:
    available_amount = float(account.equity) - float(account.last_equity)#float(account.buying_power)#state[0] // state[index+1]
    # print('available_amount:{}'.format(available_amount))
    
    
    current_price = api.get_barset(mappings[index], 'day', limit=1)
    price = current_price[mappings[index]]
    cprice = price[-1].c
    cost = action*cprice
    
    if available_amount > cost:
        print('available amount', available_amount)
        print('Submitted order: ', round(action))
        
        api.submit_order(symbol=mappings[index],qty=round(int(action)),side='buy',type='market',time_in_force='day')

        # #update balance
        state[0] = int(state[0])
        state[0] -= float(account.equity)
        # #state[index+1]*min(available_amount, action)* \
        #                     #(1+ TRANSACTION_FEE_PERCENT)

        # state[index+STOCK_DIM+1] += min(available_amount, action)

        # cost += cprice
        # state[index+1]*min(available_amount, action)* \
        #                     TRANSACTION_FEE_PERCENT
        # trades+=1
        info(cprice, 1)
    else:
        return 

def sell_stock(index, action):
    # perform sell action based on the sign of the action
    # if self.turbulence<self.turbulence_threshold:
    if state[index+STOCK_DIM+1] > 0:
        #update balance
        state[0] += account.equity
        # state[index+1]*min(abs(action),state[index+STOCK_DIM+1]) * \
        #     (1- TRANSACTION_FEE_PERCENT)

        state[index+STOCK_DIM+1] -= min(abs(action), state[index+STOCK_DIM+1])
        cost += state[index+1]*min(abs(action),state[index+STOCK_DIM+1]) * \
            TRANSACTION_FEE_PERCENT
        # trades+=1
        
        info(cprice, 1)

def makeTrades(df, model):
    '''predicts on current state using pretrained model'''
    
    # maps data
    mappings = map_stocks_index(df)

    print(mappings)
    
    # resets env
    obs_trade = reset(df)
    # print("*********************")
    # print(obs_trade)
    # print("*********************")

    for i in range(len(mappings)):
        
        actions, _states = model.predict(obs_trade)
        obs_trade, rewards, dones, info = step(actions, i, mappings, state, reward)
        
        if i == (len(mappings) - 2):
            last_state = render()

        actions = actions * HMAX_NORMALIZE
        print(actions)

    # argsort_actions = np.argsort(actions)

    # sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
    # buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]

    # portfolio = api.list_positions()

    # for index in sell_index:
    #     print('take sell action {}'.format(mappings[index]))
    #     api.submit_order(symbol=mappings[index],qty=abs(int(actions[index])),side='sell',type='market',time_in_force='day')

    # for index in buy_index:
    #     print('take buy action: {}'.format(actions[index]))
    #     api.submit_order(symbol=mappings[index],qty=int(actions[index]),side='buy',type='market',time_in_force='day')
    #     #buy_stock(index, mappings[index], data)

def step(actions, i, mappings, state, reward):
        # print(self.day)
        terminal = i >= len(mappings)
        # print(actions)

        if terminal:
            # plt.plot(self.asset_memory,'r')
            # plt.savefig('results/account_value_trade_{}_{}.png'.format(self.model_name, self.iteration))
            # plt.close()
            
            df_total_value = pd.DataFrame(asset_memory)
            # df_total_value.to_csv('results/account_value_trade_{}_{}.csv'.format(self.model_name, self.iteration))
            end_total_asset = state[0]+ \
            sum(np.array(state[1:(STOCK_DIM+1)])*np.array(state[(STOCK_DIM+1):(STOCK_DIM*2+1)]))
            print("previous_total_asset:{}".format(asset_memory[0]))

            print("end_total_asset:{}".format(end_total_asset))
            print("total_reward:{}".format(state[0]+sum(np.array(state[1:(STOCK_DIM+1)])*np.array(state[(STOCK_DIM+1):(STOCK_DIM*2+1)]))- asset_memory[0] ))
            print("total_cost: ", cost)
            print("total trades: ", trades)

            df_total_value.columns = ['account_value']
            df_total_value['daily_return']=df_total_value.pct_change(1)
            print("*********************")
            print(df_total_value['daily_return'])
            print(df_total_value['daily_return'].mean())
            print(df_total_value['daily_return'].std())
            sharpe = (4**0.5)*df_total_value['daily_return'].mean() / df_total_value['daily_return'].std()
            print("Sharpe: ",sharpe)

            df_rewards = pd.DataFrame(rewards_memory)
            #df_rewards.to_csv('results/account_rewards_trade_{}_{}.csv'.format(self.model_name, self.iteration))

            # print('total asset: {}'.format(self.state[0]+ sum(np.array(self.state[1:29])*np.array(self.state[29:]))))
            #with open('obs.pkl', 'wb') as f:
#             #    .dump(self.picklestate, f)
#             #    pickle.dump(self.state, f)

            return state, reward, terminal,{}

        else:
            # print(np.array(self.state[1:29]))

            actions = actions * HMAX_NORMALIZE
            #actions = (actions.astype(int))
            # if self.turbulence>=self.turbulence_threshold:
            #     actions=np.array([-HMAX_NORMALIZE]*STOCK_DIM)

            begin_total_asset = float(account.equity)
            # state[0]+ \
            # sum(np.array(state[1:(STOCK_DIM+1)])*np.array(state[(STOCK_DIM+1):(STOCK_DIM*2+1)]))
            #print("begin_total_asset:{}".format(begin_total_asset))

            argsort_actions = np.argsort(actions)

            sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]

            print("sell index: ", sell_index)
            for index in sell_index:
                # print('take sell action'.format(actions[index]))
                # make alpaca request
                
                positions = api.list_positions()
                
                for position in positions:
                    if position.symbol == mappings[index] and abs(int(actions[index])) >= int(position.qty) and int(position.qty) > 0:
                        print('quantity amount: ', abs(int(actions[index])))
                        print(position.symbol)
                        print('num shares owned: ', position.qty)
                        api.submit_order(symbol=mappings[index],qty=int(position.qty),side='sell',type='market',time_in_force='day')
                        sell_stock(index, actions[index])
                        


            # for index in buy_index:
            #     # print('take buy action: {}'.format(actions[index]))
            #     self._buy_stock(index, actions[index])
            #     api.submit_order(ticker, actions[index], "buy", "market", "ioc")

            for index in buy_index:
                # print('take buy action: {}'.format(actions[index]))                
                # make alpaca api request
                print('buying power: ', float(account.buying_power))
                print('num to buy: ', int(actions[index]))
                buy_stock(index, actions[index], mappings)

            # day += 1
            # data = df.loc[day,:]
            # self.turbulence = self.data['turbulence'].values[0]
            #print(self.turbulence)
            #load next state
            # print("stock_shares:{}".format(self.state[29:]))
            state =  [state[0]] + \
                    data.adjcp.values.tolist() + \
                    list(state[(STOCK_DIM+1):(STOCK_DIM*2+1)]) + \
                    data.macd.values.tolist() + \
                    data.rsi.values.tolist() + \
                    data.cci.values.tolist() + \
                    data.adx.values.tolist()

            end_total_asset = float(account.equity) - int(account.last_equity)
            # state[0]+ \
            # sum(np.array(state[1:(STOCK_DIM+1)])*np.array(state[(STOCK_DIM+1):(STOCK_DIM*2+1)]))
            asset_memory.append(end_total_asset)
            #print("end_total_asset:{}".format(end_total_asset))

            reward = end_total_asset - begin_total_asset
            # print("step_reward:{}".format(self.reward))
            rewards_memory.append(reward)

            reward = reward*REWARD_SCALING


        return state, reward, terminal, {}    
        
def reset(df, initial=True, previous_state=[]):
        if initial:
            asset_memory = [INITIAL_ACCOUNT_BALANCE]
            day = 0
            data = df.loc[day,:]
            turbulence = 0
            cost = 0
            trades = 0
            terminal = False
            #self.iteration=self.iteration
            rewards_memory = []
            #initiate state
            state = [account.buying_power] + \
                  df.adjcp.values.tolist() + \
                  [0]*STOCK_DIM + \
                  df.macd.values.tolist() + \
                  df.rsi.values.tolist() + \
                  df.cci.values.tolist() + \
                  df.adx.values.tolist()
        else:
            previous_total_asset = previous_state[0]+ \
            sum(np.array(previous_state[1:(STOCK_DIM+1)])*np.array(previous_state[(STOCK_DIM+1):(STOCK_DIM*2+1)]))
            asset_memory = [previous_total_asset]
            #self.asset_memory = [self.previous_state[0]]
            day = 0
            data = df.loc[day,:]
            turbulence = 0
            cost = 0
            trades = 0
            terminal = False
            #self.iteration=iteration
            rewards_memory = []
            #initiate state
            #self.previous_state[(STOCK_DIM+1):(STOCK_DIM*2+1)]
            #[0]*STOCK_DIM + \

            state = [account.buying_power] + \
                  df.adjcp.values.tolist() + \
                  [0]*STOCK_DIM + \
                  df.macd.values.tolist() + \
                  df.rsi.values.tolist() + \
                  df.cci.values.tolist() + \
                  df.adx.values.tolist()

        return state

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
    # data = preprocess_data(tickers, limit=2)
    # data = data[(data.datadate >= data.datadate.max())]
    # data = data.reset_index()
    # data = data.drop(["index"], axis=1)
    # data = data.fillna(method='ffill')
    # print(data)

    # state = [account.buying_power] + \
    #         data.adjcp.values.tolist() + \
    #         [0]*STOCK_DIM + \
    #         data.macd.values.tolist() + \
    #         data.rsi.values.tolist() + \
    #         data.cci.values.tolist() + \
    #         data.adx.values.tolist()

    #make trades on current stock data 
    account = api.get_account()
    makeTrades(data, model)
