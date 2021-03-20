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




def loads_model():
    '''Load in the pretrained model from the trained models folder '''
    
    pass 


def prediction(df):
    ''' predicts on current state '''
    
    action, _states = model.predict(df)
    
    obs_trade, rewards, dones, info = env_trade.step(action)
    
    
    