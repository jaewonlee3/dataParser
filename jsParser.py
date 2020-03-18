import os
import re
from pprint import pprint

jsFile = open("/Users/이재원/Documents/code/Document.js", 'r', encoding='UTF-8')
allLine = jsFile.read()
allSpl = allLine.split("$.ajax")

## Token이 될 수 있는것들: {, (, ), }
## Controller 위해 찾아야하는 것들: onWidgetAttach / Top.Controller.create / Top.Controller.get
## Function 위해 찾아야하는 것들: function(event




ControllerList = ['Top.App.onWidgetAttach', 'Top.Controller.create', 'Top.controller.get']
FunctionList = ['function(event']

#  전체 리스트를 만드는 function으로 이를 실행하면 원하고자하는 모든 리스트를 불러와야 한다.
#  Input: js파일을 input함
#  Output: Controller, Event, Ajax, SO를 모두 가져올 계획 (현재는 Ajax, SO와 이에 해당하는 Controller, Event를 모두 가져옴)
def findAll(path):
    jsFile = open(path,'r', encoding='UTF-8')
    allLine = jsFile.read()
    # Controller를 모두 찾아서 리스트화할것
    controlLevel = findController(allLine)
    # url과 Event를 담을 그릇
    urlList = []
    eventList = []
    # controller에서 각 Event, Url, SO 등을 찾아서 담기
    for co in controlLevel:
        eventLevel = findEvent(co)
        urlInfo = findUrl2(co)
        urlList = urlList + urlInfo
        for ev in eventLevel:
            urlInfo = findUrl(ev)
            urlList = urlList + urlInfo
            ev.pop('data')
        eventList = eventList + eventLevel
    pprint(urlList)
    pprint(eventList)
    jsFile.close()

# 전체 파일에서 Controller를 모두 찾고 이를 리스트화할 것
# Input: js 파일을 읽은 텍스트
# Output: Controller의 이름과 Controller가 사용되는 자바스크립트 텍스트
def findController(sentence):
   # Controller의 위치를 모두 찾을 것
   controllerObj = re.finditer('Top.App.onWidgetAttach|Top.Controller.create', sentence)
   # Controller를 담을 리스트 및 이 Controller 하의 자바스크립트 텍스트를 담을 임시로 담을 곳
   controllerList = []
   controlData = ""
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
    eventObj = re.finditer('\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?[)]', data['data'])
    # Event를 담을 리스트 및 이 Event 하의 자바스크립트 텍스트를 담을 임시로 담을 곳
    eventList = []
    eventData = ""
    dataC = data['data']
    controlName = data['name']
    for ev in eventObj:
        eventDic = {}
        eventDic['controller'] = controlName
        eventStart = ev.start()
        eventEnd = ev.end()
        eventData = dataC[eventStart:]
        evNameInter = dataC[eventStart: eventEnd]
        evNameInter2 = evNameInter.split(':')
        eventName = evNameInter2[0].strip()
        eventDic['name'] = eventName
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
        eventList.append(eventDic)
    return eventList

# 연구중
def makeDepth(path):
    jsFile = open(path, 'r', encoding='UTF-8')
    allLine = jsFile.read()
    dataList = []
    nowdataList = []
    nowdataList[0] = ""
    depth = 0
    for i in allLine:
        for j in nowdataList:
            j = j + i
        if i == '{':
            depth = depth + 1
            nowdataList[depth] = ""
            for j in nowdataList:
                j = j + i
        if i == '}':
            print(dataList[depth])
            del nowdataList[depth]
            depth = depth -1

# Iterator 개수 찾는건데 현재 안씀
def getLenIter(iterator):
   numberA = 0
   for it in iterator:
       numberA += 1
   return numberA

# Event 하에서의
def findUrl(data):
   ajaxCompile = re.compile('[$][.]ajax|Top[.]Ajax[.]execute')
   sentence = data['data']
   eventName = data['name']
   controlName = data['controller']
   abc = ajaxCompile.finditer(sentence)
   urlList = []
   for ajaxMatch in abc:
       urlDic = {}
       ajaxMatchStart = ajaxMatch.start()
       ajaxMatchEnd = ajaxMatch.end()
       urlMatch = re.search('url\s?[:]\s?[`][$]', sentence[ajaxMatchEnd:])
       if urlMatch is not None:
           urlMatchEnd = urlMatch.end()
           kk = sentence[urlMatchEnd - 2:]
           a = re.compile("`")
           urlFirst = a.search(kk)
           urlFirstLoc = urlFirst.end()
           kk1 = kk[urlFirstLoc:]
           urlEnd = a.search(kk1)
           urlSecondLoc = urlFirstLoc + urlEnd.start()
           urlSentence = kk[urlFirstLoc:urlSecondLoc]
           appVarAll, appVar = findApp(urlSentence)
           sgValue, soValue = findSGSO(urlSentence, appVarAll)
           urlDic['url'] = urlSentence
           urlDic['event'] = eventName
           urlDic['controller'] = controlName
           urlDic['app'] = appVar
           urlDic['sg'] = sgValue
           urlDic['so'] = soValue
           urlList.append(urlDic)

   return urlList


def findUrl2(data):
   eventMatch = re.search('\S+\s?[:]\s?function\s?[(]\s?\S+\s?,\s?\S+\s?[)]', data['data'])
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
       ajaxMatchStart = ajaxMatch.start()
       ajaxMatchEnd = ajaxMatch.end()
       urlMatch = re.search('url [:] [`][$]', sentence[ajaxMatchEnd:])
       if urlMatch is not None:
           urlMatchEnd = urlMatch.end()
           kk = sentence[urlMatchEnd - 2:]
           a = re.compile("`")
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
           urlDic['app'] = appVar
           urlDic['sg'] = sgValue
           urlDic['so'] = soValue
           urlList.append(urlDic)

   return urlList

def findApp(url):
   appStart = url.find('${')
   appEnd = url.find('}')
   appVarAll = url[appStart:appEnd + 1].strip()
   appVar = url[appStart + 2:appEnd]
   return appVarAll, appVar


def findSGSO(url, appVar):
   appVarTrans = appVar.replace('$', '[$]')
   appCompileFirst = re.compile('')
   soCompileEnd = re.compile('[?]action=SO')
   soCompileStart = re.compile(appVarTrans)
   abc = soCompileEnd.search(url)
   ab = soCompileStart.search(url)
   soStart = ab.end()
   soEnd = abc.start()
   sgSoValue = url[soStart:soEnd]
   sgValue = sgSoValue.split('/')[0]
   soValue = sgSoValue.split('/')[1]
   return sgValue, soValue


# for line in allSpl:
#   print(line)
#   print('--------------------------')

functionList = []
functionCompile = re.compile('\S+Logic[.]\S+[(]\s?\S+\s?[,]\s?\S+\s?[)]|\S+Logic[.]\S+[(][)]|\S+Logic[.]\S+|\S+Logic[.]\S+[(]\s?\S+\s?[)]|\S+Logic[.]\S+[(]\s?\S+\s?[,]\s?\S+\s?[)]')
aaaa = functionCompile.findall(allLine)



jsFile.close();


# findAll("/Users/이재원/Documents/code/Document.js")