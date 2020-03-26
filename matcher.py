import xmlParser
import jsParser
import os
from lxml import etree
from io import StringIO
from pprint import pprint
import csv





# Controller와 Event를 가지고 비교해야 한다.
# Event는 그냥 이름이 같은지만 비교하면 된다. 단, Event 이름이 onWidgetAttach나  init이면, js쪽의 Controller가 tlf쪽의 Event 이름과 같으면 해당 Controller에 붙여준다
# Conroller의 경우에는 tlf의 webController와 js쪽의 Controller가 같거나 tlf의 webControllerJs의 값과 js쪽의 path가 같아야 함
# 이를 모두 검색하였음에도 불구하고, 같은 값이 없는 경우에는 글로벌에서 찾아볼 것
def matchXmlAndJs(xmlList, jsList):
    totalList = []
    totalListTable = []
    for xmlDic in xmlList:
        xmlMatch = 0
        totalDic = {}
        listTable = []
        for jsDic in jsList:
            if jsDic['event'] == 'onWidgetAttach' or jsDic['event'] == 'init':
                if jsDic['controller'] == xmlDic['widgetID']:
                    xmlMatch = xmlMatch + 1
                    totalDic['xmlPath'] = xmlDic['path']
                    totalDic['parentObject'] = xmlDic['allParentObject']
                    totalDic['widget'] = xmlDic['widgetID']
                    totalDic['controller'] = jsDic['controller']
                    totalDic['event'] = jsDic['event']
                    totalDic['jsPath'] = jsDic['path']
                    totalDic['url'] = jsDic['url']
                    totalDic['app'] = jsDic['app']
                    totalDic['sg'] = jsDic['sg']
                    totalDic['so'] = jsDic['so']
                    totalList.append(totalDic)
            # path에서 src를 찾아서 src부터 찾아서 webcontrollerjs로 만들어주는게 필요함
            elif xmlDic['webController'] == jsDic['controller'] or xmlDic['webControllerJs'] == jsDic['webControllerJs']:
                if xmlDic['eventId'] == jsDic['event']:
                    xmlMatch = xmlMatch + 1
                    totalDic['xmlPath'] = xmlDic['path']
                    totalDic['parentObject'] = xmlDic['allParentObject']
                    totalDic['widget'] = xmlDic['widgetID']
                    totalDic['controller'] = jsDic['controller']
                    totalDic['event'] = jsDic['event']
                    totalDic['jsPath'] = jsDic['path']
                    totalDic['url'] = jsDic['url']
                    totalDic['app'] = jsDic['app']
                    totalDic['sg'] = jsDic['sg']
                    totalDic['so'] = jsDic['so']
                    totalList.append(totalDic)
            elif xmlDic['eventId'] == jsDic['event']:
                if jsDic['controller'] == 'FStop3062Logic' or jsDic['controller'] == 'FI_1Q_TOPLogic':
                    xmlMatch = xmlMatch + 1
                    totalDic['xmlPath'] = xmlDic['path']
                    totalDic['parentObject'] = xmlDic['allParentObject']
                    totalDic['widget'] = xmlDic['widgetID']
                    totalDic['controller'] = jsDic['controller']
                    totalDic['event'] = jsDic['event']
                    totalDic['jsPath'] = jsDic['path']
                    totalDic['url'] = jsDic['url']
                    totalDic['app'] = jsDic['app']
                    totalDic['sg'] = jsDic['sg']
                    totalDic['so'] = jsDic['so']
                    totalList.append(totalDic)
        if xmlMatch == 0:
            totalDic['xmlPath'] = xmlDic['path']
            totalDic['parentObject'] = xmlDic['allParentObject']
            totalDic['widget'] = xmlDic['widgetID']
            totalDic['controller'] = xmlDic['webController']
            totalDic['event'] = xmlDic['eventId']
            totalDic['jsPath'] = []
            totalDic['url'] =""
            totalDic['app'] =""
            totalDic['sg'] = ""
            totalDic['so'] = ""
            totalList.append(totalDic)
    for jsDic in jsList:
        jsMatch = 0
        totalDic = {}
        for xmlDic in xmlList:
            if jsDic['event'] == 'onWidgetAttach' or jsDic['event'] == 'init':
                if jsDic['controller'] == xmlDic['widgetID']:
                    jsMatch = jsMatch + 1
            elif xmlDic['webController'] == jsDic['controller'] or xmlDic['webControllerJs'] == jsDic['webControllerJs']:
                if xmlDic['eventId'] == jsDic['event']:
                    jsMatch = jsMatch + 1
            elif xmlDic['eventId'] == jsDic['event']:
                if jsDic['controller'] == 'FStop3062Logic' or jsDic['controller'] == 'FI_1Q_TOPLogic':
                    jsMatch = jsMatch + 1
        if jsMatch == 0:
            totalDic['xmlPath'] = ""
            totalDic['parentObject'] = []
            totalDic['widget'] = ""
            totalDic['controller'] = jsDic['controller']
            totalDic['event'] = jsDic['event']
            totalDic['jsPath'] = jsDic['path']
            totalDic['url'] = jsDic['url']
            totalDic['app'] = jsDic['app']
            totalDic['sg'] = jsDic['sg']
            totalDic['so'] = jsDic['so']
            totalList.append(totalDic)
    pprint(totalList)
    return totalList

def printTotal(list):
    listFile = open("C:/Users/이재원/Documents/code/matchingFile.csv", "w")
    wr = csv.writer(listFile)
    rowNum = 1
    wr.writerow([1,'xmlPath','parentWidget','widgetID','controllerId','eventId','jsPath','url','app','sg','so'])
    for Dic in list:
        rowNum = rowNum + 1
        wr.writerow([rowNum,Dic['xmlPath'],Dic['parentObject'],Dic['widget'],Dic['controller'],Dic['event'],Dic['jsPath'],Dic['url'],Dic['app'],Dic['sg'],Dic['so']])
    listFile.close()

fileList = []
jsFileList = jsParser.search("C:/Users/이재원/Documents/fsCode/FI_TOP_1Q-feature", fileList)

jsList = jsParser.readJsFile(jsFileList)

tlfFileList = []

xmlFileList = xmlParser.search("C:/Users/이재원/Documents/fsCode/FI_TOP_1Q-feature", tlfFileList)
xmlList = xmlParser.readTlfFile(xmlFileList)

kk = matchXmlAndJs(xmlList, jsList)
printTotal(kk)
