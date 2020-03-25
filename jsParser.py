import os
import re
from pprint import pprint
import copy
import json

jsFile = open("/Users/이재원/Documents/code/company.js", 'r', encoding='UTF-8')
allLine = jsFile.read()
allSpl = allLine.split("$.ajax")

## Token이 될 수 있는것들: {, (, ), }
## Controller 위해 찾아야하는 것들: onWidgetAttach / Top.Controller.create / Top.Controller.get
## Function 위해 찾아야하는 것들: function(event

# ToDo: 아예 전체 Event를 찾아야 함 (Conroller롣 알아야 함)
# ToDo: 전체 Event이름과 현재 Function의 이름을 비교해야 하고 거기서 Event이름 들 다 찾아야 함


ControllerList = ['Top.App.onWidgetAttach', 'Top.Controller.create', 'Top.controller.get']
FunctionList = ['function(event']

#  전체 리스트를 만드는 function으로 이를 실행하면 원하고자하는 모든 리스트를 불러와야 한다.
#  Input: js파일을 input함
#  Output: Controller, Event, Ajax, SO, Event 내부에서 Call하는 Event
def findAll(path, appVarList):
    pathList = findPath(path)
    jsFile = open(path,'r', encoding='UTF-8')
    allLine = jsFile.read()
    allLine = delAnnotation(allLine)
    # Controller를 모두 찾아서 리스트화할것
    controlLevel = findController(allLine)
    # 현재 파일의 모든 Event를 찾는 함수
    # ToDo: 앞으로는 모든 파일의 Event 리스트를 미리 담아놓고 거기서 가져오는 방식으로 할 것
    allEventList = findAllEvent(path)
    # url과 Event를 담을 그릇
    urlList = []
    eventList = []
    eventAllList = []
    # controller에서 각 Event, Url, SO 등을 찾아서 담기
    for co in controlLevel:
        #Controller에 있는 Event 찾기
        eventLevel = findEvent(co)
        #onWidgetAttach에 붙은 URL 찾기 + 추가
        urlInfo = findUrl2(co)
        urlList = urlList + urlInfo
        if len(urlInfo) > 0:
            for i in urlInfo:
                eventAllList.append(i)
        #Event에 있는 URL, Appvar, SG, SO 추가
        #Event에 있는 function들 중 다른 event를 호출하는데 쓰이는 function 목록 찾기
        for number, ev in enumerate(eventLevel):
            urlInfo = findUrl(ev)
            urlList = urlList + urlInfo
            ev.pop('data')
            ev.pop('var')
            ev = findEventFromFunc(ev, allEventList)
            ev.pop('func')
            eventLevel[number] = ev
        eventList = eventList + eventLevel

    # 최종 Event List 찾기
    eventAll = eventUrlMapper(eventList,urlList)
    for evAll in eventAll:
        eventAllList.append(evAll)
    for totalNum, evAll in enumerate(eventAllList):
        if str(type(evAll)) == "<class 'list'>":
            if len(evAll) > 0:
                for num, ev in enumerate(evAll):
                    for var in appVarList:
                        if 'app' in ev.keys():
                            appVar = ev['app']
                            appValue = appVar.replace(var['name'], var['value'])
                            ev['app'] = appValue
                    evAll[num] = ev
                eventAllList[totalNum] = evAll
        elif str(type(evAll)) == "<class 'dict'>":
            for var in appVarList:
                if 'app' in evAll.keys():
                    appVar = evAll['app']
                    appValue = appVar.replace(var['name'], var['value'])
                    evAll['app'] = appValue
            evAll['path'] = pathList
            eventAllList[totalNum] = evAll
    eventAll_NoDump = remove_dupe_dicts(eventAllList)

    pprint(eventAll_NoDump)
    return eventAll_NoDump
    jsFile.close()

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
       tokenNum = 0
       startPoint = controlData.find('{')
       for i in controlData[startPoint:]:
           if i == '{':
               tokenNum = tokenNum + 1
               controlDataReal = controlDataReal + i
           elif i == '}':
               tokenNum = tokenNum - 1
               controlDataReal = controlDataReal + i
           else:
               controlDataReal = controlDataReal + i
           if tokenNum == 0:
               break
       controllerDic['data'] = controlDataReal
       controllerDic['Event'] = "onWidgetAttach"
       controllerList.append(controllerDic)
   for co in controllerObj:
       # Controller 정보 담을 곳 만들기
       controllerDic = {}
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
       tokenNum = 0
       startPoint = controlData.find('{')
       for i in controlData[startPoint:]:
           if i == '{':
               tokenNum = tokenNum + 1
               controlDataReal = controlDataReal + i
           elif i == '}':
               tokenNum = tokenNum - 1
               controlDataReal = controlDataReal + i
           else:
               controlDataReal = controlDataReal + i
           if tokenNum == 0:
               break
       controllerDic['data'] = controlDataReal
       controllerList.append(controllerDic)
   return controllerList

# Controller 하에서 생성한 Event 찾고 이를 리스트화 할 것
# Input: Controller 리스트
# Output: Event 이름 및 이에 해당하는 자바 스크립트가 포함된 리스트
def findEvent(data):
    # Event의 위치를 모두 찾을 것
    eventObj = re.finditer('[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?[)]|init\s?[:]\s?function[(]\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?[)]', data['data'])
    # Event를 담을 리스트 및 이 Event 하의 자바스크립트 텍스트를 담을 임시로 담을 곳
    eventList = []
    eventData = ""
    dataC = data['data']
    controlName = data['name']
    eventNameList= []
    for ev in eventObj:
        #Event의 controller 이름과 Event 이름을 Event Dictionary에 담기
        eventDic = {}
        eventDic['controller'] = controlName
        eventStart = ev.start()
        eventEnd = ev.end()
        eventData = dataC[eventStart:]
        evNameInter = dataC[eventStart: eventEnd]
        evNameInter2 = evNameInter.split(':')
        eventName = evNameInter2[0].strip()
        eventDic['event'] = eventName
        # tokenNum은 {와 }를 통해 세어지며 {가 나오면 tokenNum이 늘고 }가 나오면 tokenNum이 줄어이된다.
        tokenNum = 0
        # Event의 시작부터 끝날때까지의 스크립트를 모두 담기
        eventDataReal = ""
        startPoint = eventData.find('{')
        for i in eventData[startPoint:]:
            if i == '{':
                tokenNum = tokenNum + 1
                eventDataReal = eventDataReal + i
            elif i == '}':
                tokenNum = tokenNum - 1
                eventDataReal = eventDataReal + i
            else:
                eventDataReal = eventDataReal + i
            if tokenNum == 0:
                break
        eventDic['data'] = eventDataReal
        #Event에 있는 function으로 보이는 것들을 모두 담기
        eventDic['func'] = findAllFunction(eventDic['data'])
        #Event에서 변수로 보이는 것들 모두 담기
        eventDic['var'] = findAllVariable(eventDic['data'])
        #Event의 Function들을 변수를 용해서 값 치환
        eventDic['func'] = matchVarFunc(eventDic['var'], eventDic['func'])
        #Event List에 정보 담기
        eventList.append(eventDic)
    return eventList

# 블록별로 찾기였으나, 자바스크립트는 지역변수가 블록별이 아니라 함수별로 지정되서 사용하지 않기로 됨
def makeDepth(path):
    jsFile = open(path, 'r', encoding='UTF-8')
    allLine = jsFile.read()
    dataListAll = []
    dataList = []
    nowdataList = []
    nowdataList.append('')
    depth = 0
    ddss = "qqq{dfds{ffsss{aaass{qqweq}fff{were}ffs}dda}wwwww}sssaa{fdss}qqwww"
    for stri in ddss:
        number = 0
        for j in nowdataList:
            j = j + stri
            nowdataList[number] = j
            number = number + 1
        if stri == '{':
            depth = depth + 1
            nowdataList.append('')
            nowdataList[depth] = '{'
        if stri == '}':
            dataList.append(nowdataList[depth])
            del nowdataList[depth]
            depth = depth - 1
            if depth == 0:
                dataList.append(nowdataList[0])
                del nowdataList[depth]
                nowdataList.append('')
                dataListAll.append(dataList)
                del dataList
                dataList = []

# Iterator 개수 찾는건데 현재 안씀
def getLenIter(iterator):
   numberA = 0
   for it in iterator:
       numberA += 1
   return numberA

# Event 하에서의 URL 정보 찾기
# Input: Event 정보
# Output: Ajax의 URL, Event 이름, Controller 이름, app, sg, so
def findUrl(data):

   # Event 정보에서 data, event 이름, controller 이름 가져오기
   sentence = data['data']
   eventName = data['event']
   controlName = data['controller']
   # ajax를 모두 찾을 것
   ajaxCompile = re.compile('[$][.]ajax|Top[.]Ajax[.]execute')
   abc = ajaxCompile.finditer(sentence)
   # url 담을 그릇
   urlList = []
   # ajax의 url 찾기
   for ajaxMatch in abc:
       urlDic = {}
       #ajax에서 url 찾기
       ajaxMatchStart = ajaxMatch.start()
       ajaxMatchEnd = ajaxMatch.end()
       urlMatch = re.search("url\s?[:]\s?[`][$]|url\s?[:]\s?'h", sentence[ajaxMatchEnd:])
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

# findURL과 비슷하나 Event 하가 아니라 Controller 하에서 바로 시작함
# Input: Controller 정보
# Output: Ajax의 URL, Event 이름, Controller 이름, app, sg, so
def findUrl2(data):
   eventMatch = re.search('[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?[)]|init\s?[:]\s?function[(]\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?[)]', data['data'])
   ajaxCompile = re.compile('[$][.]ajax|Top[.]Ajax[.]execute')
   if eventMatch is None:
       sentence = data['data']
   else:
       eventStart = eventMatch.start()
       sentence = data['data'][:eventStart]
   controlName = data['name']
   abc = ajaxCompile.finditer(sentence)
   urlList = []
   for ajaxMatch in abc:
       urlDic = {}
       # ajax에서 url 찾기
       ajaxMatchStart = ajaxMatch.start()
       ajaxMatchEnd = ajaxMatch.end()
       urlMatch = re.search("url\s?[:]\s?[`][$]|url\s?[:]\s?'h", sentence[ajaxMatchEnd:])
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


# for line in allSpl:
#   print(line)
#   print('--------------------------')

#직접적으로 언급하는 ~Logic.~() Function들 찾기
#input: javascript function
#output: Logic이 직접 언급되는 function
def findSpecialFunction(data):
    functionCompile = re.compile('[A-Za-z]\S+Logic[.]\S+[(]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z]\S+Logic[.]\S+[(][)]|[A-Za-z]\S+Logic[.]\S+|[A-Za-z]\S+Logic[.]\S+[(]\s?\S+\s?[)]|[A-Za-z]\S+Logic[.]\S+[(]\s?\S+\s?[,]\s?\S+\s?[)]')
    functionList = functionCompile.findall(data)
    return functionList
#Function으로 예상되는 것들 다 찾기
#input: javascript 텍스트
#output: function의 이름과 시작지점
def findAllFunction(data):
    # 사용된 정규식: ~.~() or ~.~; or ~.~(변수) or ~.~(변수, 변수) 단, 괄호 밖은 영문자로 시작하며 영문자,숫자, _, .만 있는 변수를 사용
    allFunctionCompile = re.compile('[A-Za-z][\w.]+[.][\w.]+[(]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z][\w.]+[.][\w.]+[(]\s?\S+\s?[)]|[A-Za-z][\w.]+[.][\w.]+[(][)]|[A-Za-z][\w.]+[.][\w.]+[;]')
    allFunction = allFunctionCompile.finditer(data)
    allFunctionList = []
    for kk in allFunction:
        FunctionDic = {}
        funcStart = kk.start();
        funcWord = kk.group();
        FunctionDic['start'] = funcStart
        FunctionDic['name'] = funcWord
        allFunctionList.append(FunctionDic)
    return allFunctionList

#변수로 예상되는 것들 다 찾기
#input: javascript 텍스트
#output: 변수의 이름과 값과 시작지점
def findAllVariable(data):
    variableList = []
    # 사용된 정규식: ~ = ~(변수, 변수), ~ = ~(변수), ~ = ~() ~ = ~; 단, 좌변은 영문자로 시작하도록
    variableCompile = re.compile(
        '[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(]\s?\S+\s?[)]|[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(][)]|[A-Za-z]\S+(?![?])\s[=]\s?[A-Za-z]\S+[;]')
    varIter = variableCompile.finditer(data)
    for var in varIter:
        totalValue = var.group()
        varStart = var.start(0)
        variableDic = {}
        totalValueSplit = totalValue.split("=")
        variableDic['name'] = totalValueSplit[0].rstrip()
        variableDic['value'] = totalValueSplit[1].lstrip().rstrip(';')
        variableDic['start'] = varStart
        variableList.append(variableDic)
    return variableList

#Function 내에 사용된 변수들을 치환
#input: javascript 텍스트
#output: 변수의 이름과 값과 시작지점
def matchVarFunc(varList, funcList):
    for number, func in enumerate(funcList):
        for var in varList:
            varName = var['name']
            varValue = var['value']
            varStart = var['start']
            if varStart < func['start']:
                funcValue = func['name'].replace(varName, varValue)
                func['name'] = funcValue
                funcList[number] = func
        func.pop('start')
    return funcList

# data 내에 있는 모든 event 이름 찾기
# 추후 변경이 필요함
def findAllEvent(data):
    events = re.finditer('[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?[)]|init\s?[:]\s?function[(]\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?[)]', data)
    eventAll = []
    for ev in events:
        eventDic = {}
        eventName = ev.group(0)
        eventStart = ev.start()
        eventSplit = eventName.split(':')
        eventValue = eventSplit[0].strip()
        eventData = data[eventStart:]
        tokenNum = 0
        eventDataReal = ""
        startPoint = eventData.find('{')
        for i in eventData[startPoint:]:
            if i == '{':
                tokenNum = tokenNum + 1
                eventDataReal = eventDataReal + i
            elif i == '}':
                tokenNum = tokenNum - 1
                eventDataReal = eventDataReal + i
            else:
                eventDataReal = eventDataReal + i
            if tokenNum == 0:
                break
        eventDic['data'] = eventDataReal
        eventDic['event'] = eventValue
        eventAll.append(eventDic)
    return eventAll

# Event List와 UrlList 매칭
def eventUrlMapper(eventList, urlList):
    eventAllList = []
    for ev in eventList:
        evMatch = 0
        for url in urlList:
            if ev['event'] == url['event']:
                evMatch = evMatch + 1
                url['callEvent'] = ev['callEvent']
                eventAllList.append(url)
        if evMatch == 0:
            eventAllList.append(ev)
    return eventAllList

# Function이름 중 Event 뽑아내기
# TODO: URL까지 다 뽑아내야 함
def findEventFromFunc(eventDic, eventAll):
    callEventList = {}
    for func in eventDic['func']:
        for event in eventAll:
            eventMatch = re.search(event['event'], func['name'])
            if eventMatch is not None:
                callEventList['callEvent'] = event['event']
    eventDic['callEvent'] = callEventList
    return eventDic

def eventUrlMapper2(eventList, urlList):
    eventAllList = []
    for ev in eventList:
        evMatch = 0
        for url in urlList:
            if ev['event'] == url['event']:
                evMatch = evMatch + 1
                eventAllList.append(url)
        if evMatch == 0:
            eventAllList.append(ev)
    return eventAllList

def findAllEvent(path):
    jsFile = open(path,'r', encoding='UTF-8')
    allLine = jsFile.read()
    # Controller를 모두 찾아서 리스트화할것
    controlLevel = findController(allLine)
    # 현재 파일의 모든 Event를 찾는 함수
    # ToDo: 앞으로는 모든 파일의 Event 리스트를 미리 담아놓고 거기서 가져오는 방식으로 할 것
    # url과 Event를 담을 그릇
    urlList = []
    eventList = []
    # controller에서 각 Event, Url, SO 등을 찾아서 담기
    for co in controlLevel:
        #Controller에 있는 Event 찾기
        eventLevel = findEvent(co)
        #onWidgetAttach에 붙은 URL 찾기 + 추가
        urlInfo = findUrl2(co)
        urlList = urlList + urlInfo
        #Event에 있는 URL, Appvar, SG, SO 추가
        #Event에 있는 function들 중 다른 event를 호출하는데 쓰이는 function 목록 찾기
        for number, ev in enumerate(eventLevel):
            urlInfo = findUrl(ev)
            urlList = urlList + urlInfo
            ev.pop('data')
            ev.pop('var')
            ev.pop('func')
            eventLevel[number] = ev
        eventList = eventList + eventLevel
    # 최종 Event List 찾기
    eventAllList = eventUrlMapper2(eventList,urlList)
    jsFile.close()
    return eventAllList

# 주석 제거
# input: 자바스크립트 텍스트
# output: 자바스크립트 텍스트
def delAnnotation(allLine):
    allLine = allLine.replace('\t', '')

    newData = ""
    theNum = 0
    annoNum = 0
    for i in allLine:
        if i == '\n':
            if annoNum < 5:
                annoNum = 0
        if i == '/' and annoNum == 0:
            annoNum = 1
        elif i == '/' and annoNum == 1:
            annoNum = 2
        elif annoNum == 0 and i == '"':
            annoNum = 3
            newData = newData + i
        elif annoNum == 3 and i == '"':
            annoNum = 0
            newData = newData + i
        elif annoNum == 3 and i != '"':
            newData = newData + i
        elif annoNum == 0 and i == "'":
            annoNum = 4
            newData = newData + i
        elif annoNum == 4 and i == "'":
            annoNum = 0
            newData = newData + i
        elif annoNum == 4 and i != "'":
            newData = newData + i
        elif annoNum == 0 and i != '/':
            newData = newData + i
        elif annoNum == 1 and i != '*':
            newData = newData + '/'
            newData = newData + i
            annoNum = 0
        elif annoNum == 1 and i == '*':
            annoNum = 5
        elif annoNum == 0:
            newData = newData + i
        elif annoNum == 2:
            newData = newData
        elif annoNum == 5 and i == '*':
            annoNum = 6
        elif annoNum == 6 and i == '*':
            annoNum = 5
        elif i == '/' and annoNum == 6:
            annoNum = 0
        elif annoNum == 5:
            newData = newData
        elif annoNum == 6:
            newData = newData
        else:
            newData = newData + i

    return newData

def search(dirname, fileList):
    try:
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            if os.path.isdir(full_filename):
                search(full_filename, fileList)
            else:
                ext = os.path.splitext(full_filename)[-1]
                if ext == '.js':
                    fileList.append(full_filename)
    except PermissionError:
        pass
    finally:
        return fileList

def inputVariable(path):
    jsFile = open(path, 'r', encoding='UTF-8')
    allLine = jsFile.read()
    allLine = delAnnotation(allLine)
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
        consRight = consSplit[1].replace(" ","")
        consRight = consRight.replace(';','')
        consRight = consRight.replace('\n', '')
        consRight = consRight.replace("'","")
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
    print(variables)
    return variables




def readJsFile(list):
    appVarList = inputVariable("/Users/이재원/Documents/code/variables.js")
    allList = []
    for file in list:
        listInFile = findAll(file, appVarList)
        allList = allList + listInFile
    return allList

def findPath(path):
    path2 = path.split('/')
    pathList = []
    for p in path2:
        path3 = p.split('\\')
        for i in path3:
            pathList.append(i)
    return pathList


def remove_dupe_dicts(l):
  list_of_strings = [json.dumps(d, sort_keys=True) for d in l ]
  list_of_strings = set(list_of_strings)
  return [json.loads(s)for s in list_of_strings]

# allFunctionCompile = re.compile('[A-Za-z][\w.]+[.][A-Za-z0-9_.]+[(]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z][\w.]+[.][\w.]+[(]\s?\S+\s?[)]|[A-Za-z][\w.]+[.][\w.]+[(][)]|[A-Za-z][\w.]+[.][A-Za-z0-9_.]+[;]')
# allFunction = allFunctionCompile.finditer(allLine)
# allFunctionList = []
# for kk in allFunction:
#     FunctionDic = {}
#     funcStart = kk.start();
#     funcWord = kk.group();
#     FunctionDic['start'] = funcStart
#     FunctionDic['name'] = funcWord
#     allFunctionList.append(FunctionDic)


fileList = []

kssk = search("/Users/이재원/Documents/fs", fileList)

readJsFile(kssk)



jsFile.close();


#findAll("/Users/이재원/Documents/code/pbs.js")