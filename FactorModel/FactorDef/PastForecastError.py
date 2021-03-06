#!/usr/bin/env python
#coding:utf-8
"""
  Author:  Wusf --<wushifan221@gmail.com>
  Purpose: 
  Created: 2016/1/13
"""

#----------------------------------------------------------------------
def Calc(cur,rptInfo,p,s,date,stkCode):
    """"""
    """
    计算Past EPS forecasts error
    cur:内存数据库cursor
    date:查询当日的日期和数据有效的最早日期
    stkCode：股票代码
    """      
    begDate = date[0]
    endDate = date[1]
    
    finYear = rptInfo[0]
    decDate = rptInfo[1]       
    
    sql = """
          SELECT AcctPeriod,NetProfits2Parent
          FROM FinancialPITData
          WHERE StkCode='{}'
                AND SUBSTR(AcctPeriod,5,4)='1231'
                AND DeclareDate<='{}'
          ORDER BY DeclareDate DESC LIMIT 1
          """
    cur.execute(sql.format(stkCode,decDate))
    content = cur.fetchone()
    if content==None:
        return None
    if content[0]==None or content[1]==None:
        return None
    d = content[0]
    v = content[1]
    
    sql = """
          SELECT DeclareDate,ForecastThisYearEPS
          FROM ForecastPITData
          WHERE StkCode='{}'
              AND AcctPeriod='{}'
              AND DeclareDate<='{}'
          ORDER BY DeclareDate DESC LIMIT 1
          """
    cur.execute(sql.format(stkCode,d,d[0:4]+endDate[4:]))
    content = cur.fetchone()
    if content==None:
        return None
    if content[1]==None:
        return None
    d = content[0]
    f = content[1]
    
    sql = """
          SELECT TotCap
          FROM MktCap
          WHERE StkCode='{}'
                AND Date<='{}'
          ORDER BY Date DESC LIMIT 1
          """
    cur.execute(sql.format(stkCode,d))
    content = cur.fetchone()
    if content==None:
        return None  
    s = content[0]       
    
    
    
    #print v/s/10000,f,s,p
    return (v/s/10000-f)/p