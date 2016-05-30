#!/usr/bin/env python
#coding:utf-8
"""
  Author:  Wusf --<wushifan221@gmail.com>
  Purpose: 
  Created: 2016/5/23
"""

import os,numpy
from datetime import datetime,timedelta
import sqlite3 as lite
import Tools.GetLocalDatabasePath as GetPath
import Tools.GetTradeDays as GetTrdDay
import UpdateFactorDatabase.FundamentalFactors._CalculateFactorValues as CalcFactorVals
import Tools.LogOutputHandler as LogHandler
import Configs.RootPath as Root
RootPath = Root.RootPath


########################################################################
class GetFactorValues(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self,logger=None):
        """Constructor"""
        if logger == None:
            self.logger = LogHandler.LogOutputHandler("ComputeFactorsAndZScores")
        else:    
            self.logger = logger
            
    
    #----------------------------------------------------------------------
    def LoadFactorTablesIntoMemory(self,dbNameFactor,factorTypes):
        """"""
        dbPath = GetPath.GetLocalDatabasePath()["EquityDataRefined"]
        dbPath = dbPath + dbNameFactor
        self.conn1 = lite.connect(dbPath)
        self.conn1.text_factory = str
        self.conn2 = lite.connect(":memory:")
        self.conn2.text_factory = str
        cur = self.conn2.cursor()
        cur.execute("ATTACH '{}' AS FVData".format(dbPath))
        
        self.fundamentalConn = self.conn1
        self.technicalConn = self.conn1
        self.analystConn = self.conn1
        
        if "Fundamental" in factorTypes:
            cur.execute("CREATE TABLE FundamentalFactors AS SELECT * FROM FVData.FundamentalFactors")
            cur.execute("CREATE INDEX idF ON FundamentalFactors(StkCode,Date)")
            self.fundamentalConn = self.conn2            
        if "Technical" in factorTypes:
            cur.execute("CREATE TABLE TechnicalFactors AS SELECT * FROM FVData.TechnicalFactors")
            cur.execute("CREATE INDEX idT ON TechnicalFactors(StkCode,Date)")
            self.technicalConn = self.conn2
        if "Analyst" in factorTypes:
            cur.execute("CREATE TABLE AnalystFactors AS SELECT * FROM FVData.AnalystFactors")
            cur.execute("CREATE INDEX idA ON AnalystFactors(StkCode,Date)")
            self.analystConn = self.conn2
    
    #----------------------------------------------------------------------
    def ChooseFactors(self,fundamentals,technicals,analysts):
        """"""
        self.fundamentalFactors = fundamentals
        self.technicalFactors = technicals
        self.analystFactors = analysts
        
    
    #----------------------------------------------------------------------
    def GetFactorValues(self,stkCode,date,effectiveTime):
        """"""
        curFdmt = self.fundamentalConn.cursor()
        curTech = self.technicalConn.cursor()
        curAnal = self.analystConn.cursor()

        factorValues = {}
        
        if len(self.fundamentalFactors)>0:
            _lookupDate = datetime.strptime(date,"%Y%m%d")
            _lookupLimit = _lookupDate - timedelta(days=effectiveTime)
            lookupLimit = _lookupLimit.strftime("%Y%m%d")    
            date = (lookupLimit,date)        
            begDate = date[0] 
            endDate = date[1]  
            sqlStr = ""
            for fct in self.fundamentalFactors:
                sqlStr += ','+fct 
            sql1 = """
                  SELECT AcctPeriod,DeclareDate,DeReportType
                  FROM FinancialPITData
                  WHERE StkCode='{}'
                      AND DeclareDate>='{}'
                      AND DeclareDate<='{}'
                  ORDER BY AcctPeriod DESC LIMIT 1
                  """
            curFdmt.execute(sql.format(stkCode,begDate,endDate))
            content = curFdmt.fetchone()
            rptInfo = content
            acctPeriods = rptInfo
            factorValues["Date"]=date
            if rptInfo == None:
                for i in xrange(len(self.fundamentalFactors)):
                    factorValues[self.fundamentalFactors[i]]=numpy.nan
                    factorValues["FinYear"] = numpy.nan
                    factorValues["AnnouceDate"] = ''
                    factorValues["RptType"] = ''
            else:
                for i in xrange(len(self.fundamentalFactors)):
                    factorValues["FinYear"] = rptInfo[0]
                    factorValues["AnnouceDate"] = rptInfo[1]
                    factorValues["RptType"] = rptInfo[2]                   
                    factorVal = algo.Calc(cur,rptInfo,p,s,date,stkCode)
                    if factorVal==None:
                        factorValues[self.fundamentalFactors[i]] = numpy.nan
                    else:
                        factorValues[self.fundamentalFactors[i]]=factorVal
                    
        if len(self.technicalFactors)>0:
            sqlStr = ""
            for fct in self.technicalFactors:
                sqlStr += ','+fct 
            sql2 = """
                  SELECT Date {}
                  FROM TechnicalFactors
                  WHERE StkCode='{}'
                        AND Date='{}' 
                  """   
            curTech.execute(sql2.format(sqlStr,stkCode,date[1]))
            content = curTech.fetchone()
            if content == None:
                for i in xrange(len(self.technicalFactors)):
                    factorValues[self.technicalFactors[i]]=numpy.nan
            else:
                for i in xrange(len(self.technicalFactors)):
                    if content[i+1] == None:
                        factorValues[self.technicalFactors[i]]=numpy.nan
                    else:
                        factorValues[self.technicalFactors[i]]=content[i+1]                    
                    
        return factorValues
            