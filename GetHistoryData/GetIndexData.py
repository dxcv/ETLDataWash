# -- coding: utf-8 --

'''
    大类资产配研究，获取大类指数历史数据
'''

import pandas as pd
from iFinDPy import *
from WindPy import w
from datetime import datetime
import mylog as mylog
class GetIndexData:
    def __init__(self):
        self.logger = mylog.logger

    def getData(self,indexCodeList=[],startDate = '2006-01-01',endDate = '2017-06-01',sourceFlag='wind'):
        indexDataDf = pd.DataFrame()
        if sourceFlag=='wind':
            self.logger.info('wind读取大类指数历史数据 indexDataDf%s'%endDate)
            w.start()
            indexData = w.wsd(codes=indexCodeList, fields=['close'], beginTime=startDate, endTime=endDate)
            if indexData.ErrorCode != 0:
                self.PrintInfoDemo.PrintLog(infostr='wind获取指数数据失败，错误代码： ', otherInfo=indexData.ErrorCode)
                return indexDataDf

            indexDataDf = pd.DataFrame(indexData.Data, index=indexData.Codes, columns=indexData.Times).T
            self.PrintInfoDemo.PrintLog(infostr='wind读取大类指数历史数据成功,写入本地文件indexDataDf%s.xlsx'%endDate)
        else:
            self.PrintInfoDemo.PrintLog(infostr='ifind读取大类指数历史数据 indexDataDf%s ' % endDate)
            thsLogin = THS_iFinDLogin("zszq5072", "754628")
            if thsLogin not in [0,-201]:
                self.PrintInfoDemo.PrintLog('登录ifind失败，请检查！')
                return indexDataDf

            codeListStr = ','.join(indexCodeList)
            indicators = 'ths_close_price_index'
            indicatorParams = ''
            params = 'Days:Tradedays,Fill:Previous,Interval:D'

            data = THS_DateSerial(codeListStr, indicators, indicatorParams, params, startDate, endDate)
            if data['errorcode'] != 0:
                self.PrintInfoDemo.PrintLog(infostr='ifind获取指数数据失败，错误代码： ', otherInfo=data['errorcode'])
                return indexDataDf

            tData = THS_Trans2DataFrame(data)
            thsLogout = THS_iFinDLogout()

            dfList = []
            for code, tempdf in tData.groupby(by=['thscode']):
                tempdf.set_index('time', drop=True, inplace=True)
                tempFianlDf = tempdf.rename(columns={indicators: code}).drop(labels=['thscode'], axis=1)
                dfList.append(tempFianlDf)
                indexDataDf = pd.concat(dfList, axis=1, join='inner')

            self.PrintInfoDemo.PrintLog(infostr='ifind读取大类指数历史数据成功,写入本地文件indexDataDf%s.xlsx' % endDate)

        # excelpath = r"C:\\Users\\lenovo\\PycharmProjects\\fundPortfolio\\GetHistoryData\\indexDataDf" + "%s.xlsx" % endDate
        # writer = pd.ExcelWriter(excelpath)
        # indexDataDf.to_excel(writer)
        # writer.save()
        return indexDataDf

    def getDataWindFind(self,indexCodeList=[],startDate='2006-01-01',endDate='2017-06-01'):
        indexDataDf = self.getData(indexCodeList=indexCodeList, startDate=startDate, endDate=endDate,sourceFlag='wind')
        if indexDataDf.empty:
            indexDataDf = self.getData(indexCodeList=indexCodeList, startDate=startDate, endDate=endDate,sourceFlag='ifind')
        return indexDataDf

    def getHisData(self,indexCodeList=[],startDate = '2006-01-01',endDate = '2017-06-01'):
        if not indexCodeList:
            self.PrintInfoDemo.PrintLog('未传入指数参数，请检查！')
            return
        self.PrintInfoDemo.PrintLog('获取大类历史指数数据: ',otherInfo=indexCodeList)
        self.PrintInfoDemo.PrintLog('数据最新获取日期: ', otherInfo=endDate)

        try:
            excelPath = r"C:\\Users\\lenovo\\PycharmProjects\\fundPortfolio\\GetHistoryData\\indexDataDf"+"%s.xlsx"%endDate
            indexDataDf = pd.read_excel(excelPath)
            self.PrintInfoDemo.PrintLog(infostr='本地读取大类指数历史数据 indexDataDf%s '%endDate)

            lostIndex = [indexCode for indexCode in indexCodeList if indexCode not in indexDataDf]
            if not lostIndex:
                indexDataDf = indexDataDf[indexCodeList]
            else:
                indexDataDf = self.getDataWindFind(indexCodeList=indexCodeList, startDate=startDate, endDate=endDate)
        except:
            indexDataDf = self.getDataWindFind(indexCodeList=indexCodeList,startDate=startDate,endDate=endDate)

        if indexDataDf.empty:
            self.PrintInfoDemo.PrintLog('获取历史数据失败！')
        return indexDataDf

if __name__ == '__main__':
    GetIndexDataDemo = GetIndexData()
    GetIndexDataDemo.getHisData()