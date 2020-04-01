import os
import re
from pprint import pprint
import copy
import json
import csv
import utilFunc

eventCompile = re.compile('[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?[)]|init\s?[:]\s?function[(]\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?[)]|function\s?[A-Za-z]\S+\s?[(]\s?\S+\s?,\s?\S+\s?[)]|function\s?[A-Za-z]\S+\s?[(]\s?\S+\s?[)]|function\s?[A-Za-z]\S+\s?[(][)]')
ajaxCompile = re.compile('[$][.]ajax|Top[.]Ajax[.]execute')
urlCompile = re.compile("url\s?[:]\s?[`][$]|url\s?[:]\s?'h")

def findAll(path, appVarList):
    pathList = utilFunc.findPath(path)
    jsFile = open(path, 'r', encoding = 'UTF-8')
    allLine = jsFile.read()
    # 주석을 모두 제거
    allLine = utilFunc.delAnnotation(allLine)
    # Controller를 모두 찾아서 리스트화할것
    controlLevel = findController(allLine)
    dataExcludeCon = dataExclCon(allLine)

    urlList = []
    eventList = []
    eventAllList = []
    eventOutConList = findEventNotInCon(dataExcludeCon)
    for number, ev in enumerate(eventOutConList):
        urlInfo = findUrl(ev)
        urlList = urlList + urlInfo
        ev.pop('data')
        eventOutConList[number] = ev
    eventList = eventList + eventOutConList
    for co in controlLevel:
        if 'Event' in co.keys():
            urlInOnWidget = findUrlInAttach(co)
            urlList = urlList + urlInOnWidget
            for i in urlInOnWidget:
                eventAllList.append(i)
        #Event에 있는 URL, Appvar, SG, SO 추가
        else:
            eventLevel = findEventInCon(co)
            for number, ev in enumerate(eventLevel):
                urlInfo = findUrl(ev)
                urlList = urlList + urlInfo
                ev.pop('data')
                eventLevel[number] = ev
            eventList = eventList + eventLevel
    eventAll = eventUrlMapper(eventList, urlList)
    for evAll in eventAll:
        eventAllList.append(evAll)
    inputPathAndWebControllerJS(eventAllList, pathList, appVarList)
    eventAll_NoDump = utilFunc.remove_dupe_dicts(eventAllList)
    return eventAll_NoDump
    jsFile.close()



def search(folder):
    jsFileList = []
    for (path, dir, files) in os.walk(folder):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.js':
                jsFileList.append("%s/%s" % (path, filename))
    return jsFileList


def inputPathAndWebControllerJS(jsList, pathList, appVarList):
    for number, jsDic in enumerate(jsList):
        jsDic['path'] = pathList
        if'src' in pathList:
            srcLoc = pathList.index('src')
            nowPath = ""
            pathNew = pathList[srcLoc:]
            for j in pathNew:
                if j == 'src':
                    nowPath = nowPath + j
                else:
                    nowPath = nowPath + '/' + j
            if str(type(jsDic)) == "<class 'dict'>":
                for var in appVarList:
                    if 'app' in jsDic.keys():
                        appVar = jsDic['app']
                        appValue = appVar.replace(var['name'], var['value']).rstrip('/').split('/')[-1]
                        jsDic['app'] = appValue
            jsDic['webControllerJs'] = nowPath
            jsList[number] =jsDic



def readJsFile(list):
    varPath = findVariableFolder(list)
    appVarList = inputVariable(varPath)
    allList = []
    for file in list:
        if'src' in file:
            listInFile = findAll(file, appVarList)
            allList = allList + listInFile
    return allList

def dataExclCon(sentence):
    controllerObj = re.finditer('Top.Controller.create|Top.App.onWidgetAttach', sentence)
    controllerRangeList = []
    for co in controllerObj:
        coStart = co.start()
        coEnd = co.end()
        controlData = sentence[coStart:]
        tokenNum = 0
        wordCount = 0
        startPoint = controlData.find('{')
        for i in controlData[startPoint:]:
            if i == '{':
                tokenNum = tokenNum + 1
                wordCount += 1
            elif i == '}':
                tokenNum = tokenNum -1
                wordCount += 1
            else:
                wordCount += 1
            if tokenNum == 0:
                break
        controllerRange = [coStart, coStart + startPoint + wordCount]
        controllerRangeList.append(controllerRange)
    lenRangeList = len(controllerRangeList)
    newData = ""
    if lenRangeList == 0:
        newData = sentence
    elif lenRangeList == 1:
        newData = sentence[:controllerRangeList[0][0]]
        newData = newData + sentence[controllerRangeList[0][1]:]
    else:
        newData = sentence[:controllerRangeList[0][0]]
        for i in range(1,lenRangeList):
            newData = newData + sentence[controllerRangeList[i-1][1]:controllerRangeList[i][0]]
            if i == (lenRangeList-1):
                newData = newData + sentence[controllerRangeList[i][1]:]
    return newData

# Event List와 UrlList 매칭
# Input: Event List, URL List
# Output: js 전체 리스트
def eventUrlMapper(eventList, urlList):
    eventAllList = []
    for ev in eventList:
        evMatch = 0
        for url in urlList:
            if ev['event'] == url['event']:
                evMatch = evMatch + 1
                eventAllList.append(url)
        if evMatch == 0:
            ev['sg'] = ""
            ev['so'] = ""
            ev['app'] = ""
            ev['url'] = ""
            eventAllList.append(ev)
    return eventAllList


def putInfoToCon(sentence, co, controllerDic, controlData):
    coStart = co.start()
    coEnd = co.end()
    controlDataReal = ""
    controlData = sentence[coEnd:]
    # Controller의 이름 찾아서 담기
    nameControl1 = re.search("[(]'\w+'", controlData)
    nameControl2 = re.search('[(]"\w+"', controlData)
    if nameControl1 is None:
        nameStart = nameControl2.start() + 2
        nameEnd = nameControl2.end() - 1
        controlName = controlData[nameStart: nameEnd]
    else:
        nameStart = nameControl1.start() + 2
        nameEnd = nameControl1.end() - 1
        controlName = controlData[nameStart: nameEnd]
    controllerDic['name'] = controlName
    # Controller에 해당하는 자바스크립트 텍스트 담기
    startPoint = controlData.find('{')
    # 데이터 담기
    controlDataReal = utilFunc.collectInnerScript(controlData,startPoint)
    controllerDic['data'] = controlDataReal
    return controllerDic



# 전체 파일에서 Controller를 모두 찾고 이를 리스트화할 것
# Input: js 파일을 읽은 텍스트
# Output: Controller의 이름과 Controller가 사용되는 자바스크립트 텍스트
def findController(sentence):
   # Controller의 위치를 모두 찾을 것
   controllerObj = re.finditer('Top.Controller.create', sentence)
   controllerObj2 = re.finditer('Top.App.onWidgetAttach', sentence)
   # Controller를 담을 리스트 및 이 Controller 하의 자바스크립트 텍스트를 담을 임시로 담을 곳
   controllerList = []
   controlData = ""
   for co in controllerObj2:
       # Controller 정보 담을 곳 만들기
       controllerDic = {}
       # controller관련 정보 담기
       controllerDic = putInfoToCon(sentence, co, controllerDic, controlData)
       controllerDic['Event'] = "onWidgetAttach"
       controllerList.append(controllerDic)
   for co in controllerObj:
       # Controller 정보 담을 곳 만들기
       controllerDic = {}
       # controller관련 정보 담기
       controllerDic = putInfoToCon(sentence, co, controllerDic, controlData)
       controllerList.append(controllerDic)
   return controllerList

def findEventInCon(data):
    # Event의 위치를 모두 찾을 것
    eventObj = eventCompile.finditer(data['data'])
    eventList = []
    eventData = ""
    dataC = data['data']
    controlName = data['name']
    for ev in eventObj:
        # Event의 controller 이름과 Event 이름을 Event Dictionary에 담기
        eventDic = {}
        eventDic['controller'] = controlName
        eventStart = ev.start()
        eventEnd = ev.end()
        eventData = dataC[eventStart:]
        evNameInter = dataC[eventStart: eventEnd].split(':')
        eventName = evNameInter[0].strip()
        eventDic['event'] = eventName
        startPoint = eventData.find('{')
        eventDataReal = utilFunc.collectInnerScript(eventData, startPoint)
        eventDic['data'] = eventDataReal
        # Event List에 정보 담기
        if eventDic['event'] not in ['success', 'error']:
            eventList.append(eventDic)
    return eventList

def findEventNotInCon(data):
    # Event의 위치를 모두 찾을 것
    eventObj = eventCompile.finditer(data)
    eventList = []
    for ev in eventObj:
        # Event의 controller 이름과 Event 이름을 Event Dictionary에 담기
        eventDic = {}
        eventDic['controller'] = ""
        eventStart = ev.start()
        eventEnd = ev.end()
        eventData = data[eventStart:]
        evNameInter = data[eventStart: eventEnd].split('(')
        eventName = evNameInter[0].strip().replace("function", "").strip().strip(':')
        eventDic['event'] = eventName
        startPoint = eventData.find('{')
        eventDataReal = utilFunc.collectInnerScript(eventData, startPoint)
        eventDic['data'] = eventDataReal
        # Event List에 정보 담기
        if eventDic['event'] not in ['success', 'error']:
            eventList.append(eventDic)
    return eventList


# Event 하에서의 URL 정보 찾기
# Input: Event 정보
# Output: Ajax의 URL, Event 이름, Controller 이름, app, sg, so
def findUrl(data):
   # Event 정보에서 data, event 이름, controller 이름 가져오기
   sentence = data['data']
   eventName = data['event']
   controlName = data['controller']
   # ajax를 모두 찾을 것
   ajaxIter = ajaxCompile.finditer(sentence)
   # url 담을 그릇
   urlList = []
   # ajax의 url 찾기
   for ajaxMatch in ajaxIter:
       urlDic = {}
       #ajax에서 url 찾기
       ajaxMatchEnd = ajaxMatch.end()
       urlMatch = urlCompile.search(sentence[ajaxMatchEnd:])
       if urlMatch is not None:
           # urlMatch에서 순수 url 찾아내기
           urlMatchEnd = urlMatch.end()
           kk = sentence[urlMatchEnd - 2 + ajaxMatchEnd:]
           a = re.compile("`|'")
           urlFirst = a.search(kk)
           urlFirstLoc = urlFirst.end()
           kk1 = kk[urlFirstLoc:]
           urlEnd = a.search(kk1)
           urlSecondLoc = urlFirstLoc + urlEnd.start()
           urlSentence = kk[urlFirstLoc:urlSecondLoc]
           #URL에서 app, sg, so 찾기
           appVarAll, appVar = findApp(urlSentence)
           sgValue, soValue = findSGSO(urlSentence, appVarAll)
           #정보 담아서 리스트에 추가
           urlDic['url'] = urlSentence
           urlDic['event'] = eventName
           urlDic['controller'] = controlName
           urlDic['app'] = appVar
           urlDic['sg'] = sgValue
           urlDic['so'] = soValue
           urlList.append(urlDic)

   return urlList


# findURL과 비슷하나 Event 하가 아니라 Controller 하에서 바로 시작함 (OnWidgetAttach일 때 사용)
# Input: Controller 정보
# Output: Ajax의 URL, Event 이름, Controller 이름, app, sg, so
def findUrlInAttach(data):
   controlName = data['name']
   sentence = data['data']
   ajaxIter = ajaxCompile.finditer(sentence)
   urlList = []
   for ajaxMatch in ajaxIter:
       urlDic = {}
       # ajax에서 url 찾기
       ajaxMatchStart = ajaxMatch.start()
       ajaxMatchEnd = ajaxMatch.end()
       urlMatch = urlCompile.search(sentence[ajaxMatchEnd:])
       if urlMatch is not None:
           # urlMatch에서 순수 url 찾아내기
           urlMatchEnd = urlMatch.end()
           kk = sentence[urlMatchEnd - 2 + ajaxMatchEnd:]
           a = re.compile("`|'")
           urlFirst = a.search(kk)
           urlFirstLoc = urlFirst.end()
           kk1 = kk[urlFirstLoc:]
           urlEnd = a.search(kk1)
           urlSecondLoc = urlFirstLoc + urlEnd.start()
           urlSentence = kk[urlFirstLoc:urlSecondLoc]
           appVarAll, appVar = findApp(urlSentence)
           sgValue, soValue = findSGSO(urlSentence, appVarAll)
           urlDic['url'] = urlSentence
           urlDic['controller'] = controlName
           urlDic['event'] = data['Event']
           urlDic['app'] = appVar
           urlDic['sg'] = sgValue
           urlDic['so'] = soValue
           urlList.append(urlDic)
   return urlList

# url을 받아와서 Application이 무엇인지 알기 위해 매칭할 수 있는 변수(appVar)와 SGSO찾는데 필요한 값 반환
# Input: url값
# Output: findSGSO에 넣어줄 값 + app 변수
def findApp(url):
   appStart = url.find('${')
   appEnd = url.find('}')
   if appStart != -1:
       appVarAll = url[appStart:appEnd + 1].strip()
       appVar = url[appStart + 2:appEnd]
   elif appStart == -1:
       appVarAll = url
       appSplit = url.split('/')
       appVar = 'http://' + appSplit[2] + '/' + appSplit[3]
   return appVarAll, appVar

# findApp으로 찾은 appVarAll에서 SG와 SO 찾음
# Input: url값
# Output: SG, SO 값
def findSGSO(url, appVar):
   appVarTrans = appVar.replace('$', '[$]')
   appCompileFirst = re.compile('')
   soCompileStart = re.compile(appVarTrans)
   ab = soCompileStart.search(url)
   if ab is not None:
       soStart = ab.end()
       sgSoValue = url[soStart:]
       sgValue = sgSoValue.split('/')[0]
       soValue = sgSoValue.split('/')[1].replace("?action=", "")
   else:
       appSplit = appVar.split('/')
       sgValue = appSplit[4]
       soValue = appSplit[5].replace("?action=", "")
   return sgValue, soValue

# app Value를 찾을 글로벌 변수들을 찾아줌
def inputVariable(path):
    jsFile = open(path, 'r', encoding='UTF-8')
    allLine = jsFile.read()
    allLine = utilFunc.delAnnotation(allLine)
    consVarCompile = re.compile('const\s?\S+\s?=\s?\S+\s?')
    consVars = consVarCompile.finditer(allLine)
    variables = []
    for consVar in consVars:
        consDic = {}
        consStart = consVar.start()
        consData = allLine[consStart:]
        cc = consData.find('\n')
        consDic['start'] = consStart
        consValue = consData[:cc-1]
        consSplit = consValue.split('=')
        consLeft = consSplit[0].replace(" ","")
        consDic['name'] = consLeft[5:]
        consRight = consSplit[1].replace(" ","").replace(';','').replace('\n', '').replace("'","")
        consDic['value'] = consRight
        variables.append(consDic)
    for number, var in enumerate(variables):
        for newVar in variables:
            varName = newVar['name']
            varValue = newVar['value']
            varStart = newVar['start']
            if varStart < var['start']:
                var['value'] = var['value'].replace(varName, varValue)
            var['value'] = var['value'].replace("+","")
            variables[number] = var
    return variables

def findVariableFolder(theList):
    varValue = ""
    for full_filename in theList:
        file_name = os.path.split(full_filename)[-1]
        if file_name == 'variables.js':
            varValue = full_filename
    return varValue

def printTotal(list):
    listFile = open("C:/Users/이재원/Documents/code/jsList3.csv", "w")
    wr = csv.writer(listFile)
    rowNum = 1
    wr.writerow([1,'jsPath','controllerId','eventId','url','app','sg','so','webControllerJs'])
    for Dic in list:
        rowNum = rowNum + 1
        wr.writerow([rowNum,Dic['path'],Dic['controller'],Dic['event'],Dic['url'],Dic['app'],Dic['sg'],Dic['so'],Dic['webControllerJs']])


# # "C:/Users/이재원/Documents/FI_TOP_1Q-feature"
# fileList = []
# jsFileList = search("C:/Users/이재원/Documents/FI_TOP_1Q-feature")
# jsList = readJsFile(jsFileList)
#
#
# # pprint(jsList)
# printTotal(jsList)




# appVar = inputVariable("/Users/이재원/Documents/code/variables.js")
#
# jsFile.close();