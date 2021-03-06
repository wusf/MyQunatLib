#!/usr/bin/env python
#coding:utf-8
"""
  Author:  Wusf --<wushifan221@gmail.com>
  Purpose: 
  Created: 2016/6/14
"""

import numpy as np
import pandas as pd


#----------------------------------------------------------------------
def Calc(df):
    """
    计算20日价格波动率
    """
    res = pd.rolling_std(np.log(df["price_adj"]),20).to_frame("PVolatility20d")
    return res