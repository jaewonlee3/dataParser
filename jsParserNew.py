import os
import re
from pprint import pprint
import copy
import json
import csv
import utilFunc

eventCompile = re.compile('[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?[)]|init\s?[:]\s?function[(]\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?\S+\s?[)]|[A-Za-z]\S+\s?[:]\s?function\s?[(]\s?[)]|function\s?[A-Za-z]\S+\s?[(]\s?\S+\s?,\s?\S+\s?[)]|function\s?[A-Za-z]\S+\s?[(]\s?\S+\s?[)]|function\s?[A-Za-z]\S+\s?[(][)]')
ajaxCompile = re.compile('[$][.]ajax|Top[.]Ajax[.]execute')
urlCompile = re.compile("url\s?[:]\s?[`][$]|url\s?[:]\s?'|url\s?[:]\s?[A-Za-z]\S+")
variableCompile = re.compile(
        '[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(]\s?\S+\s?[,]\s?\S+\s?[,]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(]\s?\S+\s?[,]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(]\s?\S+\s?[)]|[A-Za-z]\S+\s?[=]\s?[A-Za-z]\S+[(][)]|[A-Za-z]\S+(?![?])\s[=]\s?\S+[;]')
controllerCompile = re.compile('Top.Controller.create|Top.App.onWidgetAttach')
allFunctionCompile = re.compile('[A-Za-z][\w.]+[.][\w.]+[(]\s?\S+\s?[,]\s?\S+\s?[,]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z][\w.]+[.][\w.]+[(]\s?\S+\s?[,]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z][\w.]+[.][\w.]+[(]\s?\S+\s?[,]\s?\S+\s?[)]|[A-Za-z][\w.]+[.][\w.]+[(]\s?\S+\s?[)]|[A-Za-z][\w.]+[(]\s?\S+\s?,\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z][\w.]+[(]\s?\S+\s?,\s?\S+\s?[)]|[A-Za-z][\w.]+[(]\s?\S+\s?[)]|[A-Za-z][\w.]+[(][)]')
controllerCompile2 = re.compile('Top.Controller.create')
controllerGetCompile = re.compile('Top.Controller.get')


# input: 파일의 위치 텍스트, 해당 app의 변수 리스트
# output: js파일의 정보를 담은 리스트
# 해당 js 파일에 있는 controller, event, url, app, sg, so 정보 가져올 것
def findAll(path, appVarList, allEventList, allVarList, allUrlList):
    # 경로 텍스트를 뎁스 별로 나눠서 리스트화
    pathList = utilFunc.findPath(path)
    # 해당 파일의 텍스트를 모두 읽어오기
    jsFile = open(path, 'r', encoding = 'UTF-8')
    allLine = jsFile.read()
    # 주석을 모두 제거
    allLine = utilFunc.delAnnotation(allLine)
    # Controller를 모두 찾아서 리스트화할것
    controlLevel = findController(allLine, allVarList)
    # url과 event, 전체 정보를 담을 리스트 생성
    urlList = []
    eventList = []
    eventAllList = []
    # Controller 안에 있는 Event들 찾아서 정보 담아올 것
    for co in controlLevel:
        if 'event' in co.keys():
            urlInOnWidget = findUrl(co)
            urlList = urlList + urlInOnWidget
            for i in urlInOnWidget:
                eventAllList.append(i)
        #Event에 있는 URL, Appvar, SG, SO 추가
        else:
            eventLevel = findEventInCon(co, allVarList)
            for number, ev in enumerate(eventLevel):
                urlInfo = findUrl(ev)
                urlList = urlList + urlInfo
                ev.pop('data')
                ev['callEvent'] = findEventFromFunc(ev, allEventList)
                eventLevel[number] = ev
                lenCallEv = len(ev['callEvent'])
                urlCall = findUrlFromCallEvent(ev,allUrlList)
                lenUrlCall = len(urlCall)
                # if lenCallEv > 0:
                #     print(path)
                #     print(ev['callEvent'])
                #     print(ev['event'])
                ev.pop('var')
                urlList = urlList + urlCall
            eventList = eventList + eventLevel
    # Event 리스트와 url 리스트를 매핑해서 전체 리스트에 담을 것
    eventUrlMapper(eventList, urlList, eventAllList)
    # 최종 리스트에 WebControllerJS, Path 넣을 것
    inputPathAndWebControllerJS(eventAllList, pathList, appVarList)
    # 중복 리스트 제거할 것
    eventAll_NoDump = utilFunc.remove_dupe_dicts(eventAllList)
    return eventAll_NoDump
    jsFile.close()


# input: js 파일이 들어 있는 리스트
# output: 모든 js파일의 정보를 담은 리스트
# 리스트의 모든 js 파일에 있는 controller, event, url, app, sg, so 정보 가져올 것
def readJsFile(list):
    # 글로벌 변수들이 담겨져 있는 파일로부터 app 변수를 받아 오기
    varPath = findVariableFolder(list)
    appVarList = inputVariable("C:/Users/이재원/Documents/FI_TOP_1Q-feature/FI_1Q_TOP/src/common/variables.js")
    # 모든 js 파일을 돌면서,이벤트 리스트, url 리스트, 변수 리스트를 가져올 것
    eventList, urlList, varList = findAllEvFuncVar(list)
    allList = []
    # 모든 js 파일들을 돌면서 js파일들의 정보를 담은 리스트를 가져올 것
    for file in list:
        if 'src' in file:
            listInFile = findAll(file, appVarList, eventList, varList, urlList)
            allList = allList + listInFile
    return allList

# input: 값을 삽입할 리스트, path 리스트, app 변수 리스트
# output: path, webControllerJS, app 변수 값을 삽입한 리스트
# webControllerJs, path를 각 딕셔너리에 넣고 app 변수 값을 미리 설정해둔 값으로 변환
def inputPathAndWebControllerJS(jsList, pathList, appVarList):
    # 리스트의 딕셔너리들을 하나씩 돌면서 path, app, webControllerJs 값을 넣어줌
    for number, jsDic in enumerate(jsList):
        # 'path' 정보 담기
        jsDic['path'] = pathList

        # src 폴더부터 현재 파일까지의 경로를 담으면 webControllerJs가 됨
        if'src' in pathList:
            srcLoc = pathList.index('src')
            nowPath = ""
            pathNew = pathList[srcLoc:]
            for j in pathNew:
                if j == 'src':
                    nowPath = nowPath + j
                else:
                    nowPath = nowPath + '/' + j
            # 기존의 app 값을 미리 담아둔 변수리스트를 이용하여 값을 변환하고 거기서 진짜 app 값을 추출
            if str(type(jsDic)) == "<class 'dict'>":
                for var in appVarList:
                    if 'app' in jsDic.keys():
                        appVar = jsDic['app']
                        appValue = appVar.replace(var['name'], var['value']).rstrip('/').split('/')[-1]
                        jsDic['app'] = appValue
            # webControllerJS의 값을 넣기
            jsDic['webControllerJs'] = nowPath
            jsList[number] =jsDic





# input: 전체 javascript
# output: 컨트롤러 바깥에 있는 javascript text
# 컨트롤러 바깥에 있는 javascript 텍스트만을 따로 구하는 함수로, 전역 함수들을 찾기위한 방법
def dataExclCon(sentence):
    # 전체 스크립트에서 Controller들 찾기
    controllerObj = controllerCompile2.finditer(sentence)
    controllerRangeList = []
    # 각 Controller가 스크립트에서 점유하고 있는 텍스트 위치 표시
    for co in controllerObj:
        coStart = co.start()
        coEnd = co.end()
        controlData = sentence[coStart:]
        # tokenNum => { 일경우 + 1, } 일경우 -1 해서 데이터를 열었을 때부터 데이터를 닫을 때까지...
        # wordCount => 문자가 몇번째인지 위치를 적어주는 것
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
        # controller에 속해있는 데이터가 어디부터 어디까지 위치 되어 있는지를 표기
        controllerRange = [coStart, coStart + startPoint + wordCount]
        controllerRangeList.append(controllerRange)
    # js 파일 내의 컨트롤러 개수 구하기
    lenRangeList = len(controllerRangeList)
    newData = ""
    # 컨트롤러가 점유하고 있지 않는 텍스트들을 이어 컨트롤러 밖의 텍스트를 새로 만들기
    # js 파일 내의 컨트롤러 개수에 따라 텍스트를 잇는 방법이 달라짐
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
def eventUrlMapper(eventList, urlList, eventAllList):
    for ev in eventList:
        evMatch = 0
        for url in urlList:
            if ev['event'] == url['event']:
                evMatch = evMatch + 1
                eventAllList.append(url)
        if evMatch == 0:
            eventAllList.append(ev)


# 전체 파일에서 Controller를 모두 찾고 이를 리스트화할 것
# Input: js 파일을 읽은 텍스트
# Output: Controller의 이름과 Controller가 사용되는 자바스크립트 텍스트
def findController(sentence, allVarList):
   # Controller의 위치를 모두 찾을 것
   controllerObj = controllerCompile.finditer(sentence)
   # Controller를 담을 리스트 및 이 Controller 하의 자바스크립트 텍스트를 담을 임시로 담을 곳
   controllerList = []
   controlData = ""
   for co in controllerObj:
       # Controller 정보 담을 곳 만들기
       controllerDic = {}
       # controller관련 정보 담기

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
       controlDataReal = utilFunc.collectInnerScript(controlData, startPoint)
       controllerDic['data'] = controlDataReal
       if co.group() == "Top.App.onWidgetAttach":
           controllerDic['event'] = "onWidgetAttach"
           controllerDic['func'] = findAllFunction(controllerDic['data'])
           controllerDic['var'] = findAllVar(controllerDic['data'], controllerDic['name']) + allVarList
           controllerDic['func'] = matchVarFunc(controllerDic['var'], controllerDic['func'], controllerDic['name'])
       # controller에 관한 정보를 담은 딕셔너리를 controller List에 담기
       controllerList.append(controllerDic)
   return controllerList

# Input: Controller 관련 자바 스크립트
# Output: Event의 이름과 해당 함수 이름 및 자바 스크립트 전부
# Controller에 있는 자바스크립트 텍스트를 모두 읽어서 거기서 Event와 관련된 정보를 뽑아내는 함수
def findEventInCon(data, allVarList):
    # Event의 위치를 모두 찾을 것
    eventObj = eventCompile.finditer(data['data'])
    eventList = []
    eventData = ""
    dataC = data['data']
    for ev in eventObj:
        # Event의 controller 이름과 Event 이름을 Event Dictionary에 담기
        eventDic = {}
        eventDic['controller'] = data['name']
        eventStart = ev.start()
        eventEnd = ev.end()
        eventData = dataC[eventStart:]
        evNameInter = dataC[eventStart: eventEnd].split(':')
        eventName = evNameInter[0].strip()
        eventDic['event'] = eventName.strip()
        eventDic['sg'] = ""
        eventDic['so'] = ""
        eventDic['app'] = ""
        eventDic['url'] = ""
        # Event에 관
        startPoint = eventData.find('{')
        eventDataReal = utilFunc.collectInnerScript(eventData, startPoint)
        eventDic['data'] = eventDataReal
        eventDic['func'] = findAllFunction(eventDic['data'])
        eventDic['var'] = findAllVar(eventDic['data'], eventDic['event']) + allVarList
        eventDic['func'] = matchVarFunc(eventDic['var'], eventDic['func'], eventDic['event'])
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
           urlMatchStart = urlMatch.start()
           kk = sentence[urlMatchStart + ajaxMatchEnd + 3:]
           a = re.compile("`|'")
           thisLineSplit = kk.split('\n')
           thisLine = thisLineSplit[0]
           urlSentence = thisLine.replace(':','').replace(' ','').replace(',','').strip('`').strip("'")
           #URL에서 app, sg, so 찾기
           urlMatchList = matchVarUrl(data['var'], urlSentence)
           for url in urlMatchList:
               appVarAll, appVar = findApp(url)
               sgValue, soValue = findSGSO(url, appVarAll)
               #정보 담아서 리스트에 추가
               urlDic['url'] = url
               urlDic['event'] = data['event']
               if data['event'] != "onWidgetAttach":
                   urlDic['controller'] = data['controller']
               else:
                   urlDic['controller'] = data['name']
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
   # ${FsPo} 형식인지 확인하기 위한 컴파일
   soCompileStart = re.compile(appVar.replace('$', '[$]'))
   ab = soCompileStart.search(url)
   # 형식에 따른 sg, so 값 도출
   if ab is not None:
       soStart = ab.end()
       sgSoValue = url[soStart:]
       sgValue = sgSoValue.split('/')[0]
       soValue = sgSoValue.split('/')[1].replace("?action=", "").replace("?action", "")
   else:
       appSplit = appVar.split('/')
       sgValue = appSplit[4]
       soValue = appSplit[5].replace("?action=", "")
   return sgValue, soValue


# input: global variable이 모여있는 js 파일
# output: js 파일
# app Value를 찾을 글로벌 변수들을 찾아줌
def inputVariable(path):
    # 스크립트 읽어오고 주석 제거
    jsFile = open(path, 'r', encoding='UTF-8')
    allLine = jsFile.read()
    allLine = utilFunc.delAnnotation(allLine)
    # const 유형의 변수들 찾기
    consVarCompile = re.compile('const\s?\S+\s?=\s?\S+\s?')
    consVars = consVarCompile.finditer(allLine)
    variables = []
    for consVar in consVars:
        # cons 유형의 변수들에 대한 정보 추가
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
    # 값들 중 앞에서 지정된 변수를 포함하는 것들이 있으면 변수 이름을 값으로 대체
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


# input: js 파일들이 모여있는 리스트
# output: 글로벌 변수들이 들어있는 파일 이름
# 전체 js 파일 리스트에서 글로벌 변수들이 모여있는 파일 이름 찾아오기
def findVariableFolder(theList):
    varValue = ""
    for full_filename in theList:
        file_name = os.path.split(full_filename)[-1]
        if file_name == 'variables.js':
            varValue = full_filename
    return varValue


# input: js 파일 리스트
# output: csv 파일
# js 파일을 csv 파일화
def printTotal(list):
    listFile = open("C:/Users/이재원/Documents/code/jsList3.csv", "w")
    wr = csv.writer(listFile)
    rowNum = 1
    wr.writerow([1,'jsPath','controllerId','eventId','url','app','sg','so','webControllerJs'])
    for Dic in list:
        rowNum = rowNum + 1
        wr.writerow([rowNum,Dic['path'],Dic['controller'],Dic['event'],Dic['url'],Dic['app'],Dic['sg'],Dic['so'],Dic['webControllerJs']])


# input: js 파일이 있는 리스트
# output: 모든 event 리스트, 전역적 혹은 controller 전체에 사용되는 변수 리스트, 모든 url 리스트
# 모든 js 파일을 돌면서, 모든 event 리스트, global Variable List, 모든 url List를 모두 가져오기
def findAllEvFuncVar(jsList):
    eventList = []
    varList = []
    urlList = []
    for file in jsList:
        if 'src' in file:
            ev, var, url = findEvFuncVar(file)
            eventList = eventList + ev
            varList = varList + var
            urlList = urlList + url
    eventList = utilFunc.remove_dupe_dicts(eventList)
    urlList = utilFunc.remove_dupe_dicts(urlList)
    varList = utilFunc.remove_dupe_dicts(varList)
    for ev in eventList:
        print(ev['controller'])
        print(ev['event'])
        print('-------------------------------------')
    return eventList, urlList, varList





# input: js 파일 경로
# output: js 파일 내에 있는 모든 Event, 글로벌 변수 (Controller 하의 글로벌 변수까지), URL
# js 파일 내에 있는 모든 Event, 글로벌 변수 (Controller 하의 글로벌 변수까지), URL 가져오기
def findEvFuncVar(path) :
    # 변수, EVent, URL 리스트를 담을 공간
    allVarList = []
    allEventList = []
    allUrlList = []
    # js 파일 경로로부터 실제 js 파일 텍스트를 가져오고 주석을 제거 할 것
    jsFile = open(path, 'r', encoding='UTF-8')
    allLine = jsFile.read()
    allLine = utilFunc.delAnnotation(allLine)
    # Controller를 모두 찾아서 리스트화할것
    controlLevel = findController(allLine, allVarList)
    # Controller 밖에 있는 데이터만 가져오기
    dataExcludeCon = dataExclCon(allLine)
    # controller 밖에 있는 event들을 찾아서  event List에 담기
    eventOutConList = findGlobalEv(dataExcludeCon)
    # Event 밖에 있는 데이터들을 찾아서 글로벌 변수로 선언
    dataExcludeEvent = dataExclFunc(dataExcludeCon)
    globalVarList = findGlobalVar(dataExcludeEvent, 'global', path)
    allVarList = allVarList + globalVarList
    # event List의 event로부터 url, sg, so, app 등의 정보를 가져오고 리스트에 담기
    for number, ev in enumerate(eventOutConList):
        urlInfo = findUrl(ev)
        allUrlList = allUrlList + urlInfo
        ev.pop('data')
        eventOutConList[number] = ev
    allEventList = allEventList + eventOutConList
    # controller를 찾아내기
    controlLevel = findController(allLine, allVarList)
    for co in controlLevel:
        dataExcludeEventInCon = dataExclFunc(co['data'])
        # Controller 안에 있는 변수들을 찾기
        conVarList = findGlobalVar(dataExcludeEventInCon, co['name'], path)
        allVarList = allVarList + conVarList
        if 'event' in co.keys():
            co.pop('data')
        #Event에 있는 URL, Appvar, SG, SO 추가
        else:
            eventLevel = findEventInCon(co, allVarList)
            for number, ev in enumerate(eventLevel):
                urlInfo = findUrl(ev)
                allUrlList = allUrlList + urlInfo
                ev.pop('data')
                ev.pop('app')
                ev.pop('sg')
                ev.pop('so')
                ev.pop('url')
                eventLevel[number] = ev
            allEventList = allEventList + eventLevel
    return allEventList, allVarList, allUrlList


# input:js 텍스트 (controller 밖에 있어서 글로벌로 지정될 수 있는 텍스트)
# output: Event 목록 (controller = global, event 이름, event 스크립트, event 내 변수 리스트, event 내 함수 리스트)
# controller 밖에 있는 텍스트에서 Event 목록
def findGlobalEv(sentence):
    globalEvList = []
    eventObj = eventCompile.finditer(sentence)
    # Event로 예상되는 함수들 다 담기
    for ev in eventObj:
        # controller 정보, event 이름, event 내부의 data, function, 변수를 모두 event Dic 넣기
        eventDic = {}
        eventStart = ev.start()
        eventEnd = ev.end()
        eventData = sentence[eventStart:]
        evNameInter = sentence[eventStart: eventEnd].split('(')
        eventName = evNameInter[0].strip().replace("function", "").strip().strip(':')
        eventDic['controller'] = 'global'
        eventDic['event'] = eventName.strip()
        startPoint = eventData.find('{')
        eventDic['data'] = utilFunc.collectInnerScript(eventData, startPoint)
        eventDic['func'] = findAllFunction(eventDic['data'])
        eventDic['var'] = findAllVar(eventDic['data'], eventDic['event'])
        if eventDic['event'] not in ['success', 'error', 'success ', 'success  ', 'error ', 'error  ']:
            globalEvList.append(eventDic)
    return globalEvList


# input: js 텍스트, controller 이름, js 파일 경로
# output: global 변수 리스트 (변수의 이름, 값, 시작 지점, 포함된 controller 이름 (전역일경우 global), 파일 이름)
# 전체에서 쓰이는 global 변수들, controller 내에서 사용하는 controller 글로벌 변수를
def findGlobalVar(sentence, loc, path):
    globalVarList = []
    varIter = variableCompile.finditer(sentence)
    for var in varIter:
        variableDic = {}
        variableDic = inputVarInfo(var, variableDic)
        # global은 이게 전체 글로벌 변수인지 controller 하에서 글로벌 변수인지를 알려줌
        variableDic['global'] = loc
        variableDic['path'] = path
        globalVarList.append(variableDic)
    return globalVarList


# input: 변수 compile object, 변수 내용을 담을 딕셔너리
# output: 변수 내용을 담은 딕셔너리 (변수의 이름, 값, 시작 지점)
# 변수 딕셔너리에 공통적으로 넣을 정보들 넣어주는 함수
def inputVarInfo(var, variableDic):
    totalValue = var.group()
    varStart = var.start(0)
    totalValueSplit = totalValue.split("=")
    variableDic['name'] = totalValueSplit[0].rstrip()
    variableDic['value'] = totalValueSplit[1].lstrip().rstrip(';')
    variableDic['start'] = varStart
    return variableDic


# input: js 텍스트 및 event, function 이름
# output: 변수 리스트 (변수의 이름, 값, event, 시작지점)
# 특정 event(function) 내의 변수들 찾기.
def findAllVar(sentence, loc):
    varList = []
    varIter = variableCompile.finditer(sentence)
    for var in varIter:
        variableDic = {}
        variableDic['global'] = loc
        variableDic = inputVarInfo(var, variableDic)
        varList.append(variableDic)
    return varList


# input: event 명단
# output: 함수 리스트 (함수 전체, 함수 이름, 함수 input, 함수 시작 지점)
# event 내에 있는 function 리스트 모두 찾기
def findAllFunction(data):
    funcIter = allFunctionCompile.finditer(data)
    funcList = []
    for func in funcIter:
        funcDic = {}
        funcDic['start'] = func.start()
        funcAllName = func.group();
        funcSplitPoint = funcAllName.rfind('(')
        funcDic['all'] = funcAllName
        funcDic['name'] = funcAllName[:funcSplitPoint]
        funcDic['input'] = funcAllName[funcSplitPoint+1:].rstrip(')').split(',')
        funcList.append(funcDic)
    return funcList


# input: 변수 리스트, 함수 리스트, 어떤 위치에서 변수와 함수 매칭이 이뤄지는지를 알려주는 값
# output: 함수에서 변수의 이름이 변수의 값으로 전환된
# 함수 리스트의 각 함수에서 변수 이름을 찾고, 변수를 변환 (이 함수는 추후 코드 리팩토링 필요)
def matchVarFunc(varList, funcList, loc):
    for number, func in enumerate(funcList):
        for var in varList:
            # 변수 리스트에서 변수를 하나씩 확인하면서 변수가 전역변수이거나 (global 값의 global이거나) 변수의 위치가 loc와 일치하면 변수의 contain 표시를 Y로 전환
            # contain 표시가 Y인 변수들만 비교
            if 'global' in var.keys():
                if var['global'] == 'global':
                    var['contain'] = 'Y'
                elif var['global'] == loc:
                    var['contain'] = 'Y'
                else:
                    var['contain'] = 'N'
            else:
                var['contain'] = 'N'
            if var['contain'] == 'Y':
                func['name'] = func['name'].replace(var['name'], var['value'])
                funcList[number] = func
    return funcList

# input: 변수 리스트, url 주소
# output: 변수 값이 변환된 url 주소
# url이 변수로 되어 있으면 변수 이름을 이에 해당하는 값으로 변환하여 output으로 내보낼 것
def matchVarUrl(varList, urlSentence):
    urlVarMatch = []
    # url이 이미 http
    if '$' in urlSentence or 'http' in urlSentence:
        urlVarMatch.append(urlSentence)
    else:
        for var in varList:
            if var['name'] in urlSentence:
                urlVarMatch.append(urlSentence.replace(var['name'], var['value']).strip("'").strip('`'))
    return urlVarMatch


# input: event에 관한 딕셔너리, 모든 event 리스트
# output: event에서 호출한 다른 event 목록
# event 내부에 있는 함수 목록을 전체 event 리스트와 대조하여 event의 함수들 중 event를 찾아서 callEvent 목록에 넣기
def findEventFromFunc(eventDic, allEventList):
    callEventList = []
    for func in eventDic['func']:
        # 함수가 속한 controller가 event의 controller와 같거나 글로벌이고, event의 이름이 함수의 이름중에 발견되면, 이를 callEvent 목록에 추가
        theController = eventDic['controller']
        getController = controllerGetCompile.search(func['name'])
        if getController is not None:
            token = 0
            dataCon = ""
            for i in func['name'][getController.end(): ]:
                if i == '"':
                    token += 1
                else:
                    if token == 1:
                        dataCon = dataCon + i
            theController = dataCon
        for event in allEventList:
            eventMatch = re.search(event['event'].strip(), func['name'].strip())
            if eventMatch is not None:
                if event['controller'] == 'global' or event['controller'] == theController :
                    callEventList.append(event['event'])
    return callEventList


# input: event 딕셔너리, 전체 url 목록
# output: url 딕셔너리
# callEvent 내에 있는 url을 찾아서 url 딕셔너리를 만들기
def findUrlFromCallEvent(eventDic, allUrlList):
    urlList = []
    for callEv in eventDic['callEvent']:
        for urlDic in allUrlList:
            if callEv == urlDic['event']:
                newUrlDic = {}
                newUrlDic['event'] = eventDic['event']
                newUrlDic['controller'] = eventDic['controller']
                newUrlDic['url'] = urlDic['url']
                newUrlDic['app'] = urlDic['app']
                newUrlDic['sg'] = urlDic['sg']
                newUrlDic['so'] = urlDic['so']
                urlList.append(newUrlDic)
    return urlList



def dataExclFunc(sentence):
    # 전체 스크립트에서 Controller들 찾기
    eventObj = eventCompile.finditer(sentence)
    eventRangeList = []
    # 각 Controller가 스크립트에서 점유하고 있는 텍스트 위치 표시
    for ev in eventObj:
        evStart = ev.start()
        evEnd = ev.end()
        eventData = sentence[evStart:]
        tokenNum = 0
        wordCount = 0
        startPoint = eventData.find('{')
        for i in eventData[startPoint:]:
            if i == '{':
                tokenNum = tokenNum + 1
                wordCount += 1
            elif i == '}':
                tokenNum = tokenNum - 1
                wordCount += 1
            else:
                wordCount += 1
            if tokenNum == 0:
                break
        eventRange = [evStart, evStart + startPoint + wordCount]
        eventRangeList.append(eventRange)
    # 컨트롤러가 점유하고 있지 않는 텍스트들을 이어 컨트롤러 밖의 텍스트를 새로 만들기
    newData = ""
    eventRangeListReal = []
    for evRange in eventRangeList:
        evExcl = ""
        for evRange2 in eventRangeList:
            if evRange[0] > evRange2[0] and evRange[1] < evRange2[1]:
                evExcl = "Y"
        if evExcl != "Y":
            eventRangeListReal.append(evRange)
    lenRangeList = len(eventRangeListReal)
    if lenRangeList == 0:
        newData = sentence
    elif lenRangeList == 1:
        newData = sentence[:eventRangeListReal[0][0]]
        newData = newData + sentence[eventRangeListReal[0][1]:]
    else:
        newData = sentence[:eventRangeListReal[0][0]]
        for i in range(1, lenRangeList):
            newData = newData + sentence[eventRangeListReal[i - 1][1]:eventRangeListReal[i][0]]
            if i == (lenRangeList - 1):
                newData = newData + sentence[eventRangeListReal[i][1]:]
    return newData

# # "C:/Users/이재원/Documents/FI_TOP_1Q-feature"
# # fileList = []
# jsFileList = utilFunc.search("C:/Users/이재원/Documents/FI_TOP_1Q-feature/FI_1Q_TOP/", ".js")
# jsList = readJsFile(jsFileList)
#
#
# # for k in jsList:
# #     pprint(k)
# printTotal(jsList)




# appVar = inputVariable("/Users/이재원/Documents/code/variables.js")
#
# jsFile.close();