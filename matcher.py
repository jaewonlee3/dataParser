import xmlParser
import jsParserNew
import utilFunc
import csv





# Controller와 Event를 가지고 비교해야 한다.
# Event는 그냥 이름이 같은지만 비교하면 된다. 단, Event 이름이 onWidgetAttach나  init이면, js쪽의 Controller가 tlf쪽의 Widget 이름과 같으면 해당 Controller에 붙여준다
# Conroller의 경우에는 tlf의 webController와 js쪽의 Controller가 같거나 tlf의 webControllerJs의 값과 js쪽의 path가 같아야 함
# 이를 모두 검색하였음에도 불구하고, 같은 값이 없는 경우에는 글로벌에서 찾아볼 것
# input: tlf파서의 결과물(xmlList), js파서의 결과물(jsList)
# output: 두 결과물이 매칭된 리스트 형태
def matchXmlAndJs(xmlList, jsList):
    # 전체 리스트 담을 곳
    totalList = []
    # xmlList와 jsList의 결과물들을 하나씩 뽑아와서 비교

    for xmlDic in xmlList:
        # jsList와 매칭된 xml리스트와 매칭되지 않은 xml리스트 구분용
        xmlMatch = 0
        # 매칭 결과를 담을 Dictionary
        for jsDic in jsList:
            # Event 이름이 onWidgetAttach나 init일 경우, js쪽의 Controller와 tlf쪽의 widget 이름이 같으면 매칭한 후 이를 리스트에 올려줄 것
            if jsDic['event'] == 'onWidgetAttach':
                if jsDic['controller'] == xmlDic['widgetID']:
                    totalDic = {}
                    xmlMatch = xmlMatch + 1
                    totalDic = inputValueFormal(totalDic, jsDic, xmlDic)
                    totalList.append(totalDic)
            # tlf의 webController와 js쪽의 controller가 같거나 tlf의 webControllerJs와 js의 path가 같고, tlf의 event와 js의 event가 같아야함
            elif xmlDic['webController'] == jsDic['controller'] or xmlDic['webControllerJs'] == jsDic['webControllerJs']:
                if xmlDic['eventId'] == jsDic['event'] and jsDic != 'onWidgetAttach':
                    totalDic = {}
                    xmlMatch = xmlMatch + 1
                    totalDic = inputValueFormal(totalDic, jsDic, xmlDic)
                    totalList.append(totalDic)
            # tlf쪽과 js쪽의 event 이름이 가트며, event가 global event
            elif xmlDic['eventId'] == jsDic['event']:
                if jsDic['controller'] == 'FStop3062Logic' or jsDic['controller'] == 'FI_1Q_TOPLogic':
                    totalDic = {}
                    xmlMatch = xmlMatch + 1
                    totalDic = inputValueFormal(totalDic, jsDic, xmlDic)
                    totalList.append(totalDic)
        # js와 매칭되지 않은 tlf쪽의 리스트들을 넣어줌
        if xmlMatch == 0:
            totalDic = {}
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
            totalDic['matching'] = "N"
            totalList.append(totalDic)
    # xmlList와 jsList의 결과물들을 하나씩 뽑아와서 비교
    for jsDic in jsList:
        jsMatch = 0
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
        # tlf와 매칭되지 않은 js쪽의 리스트들을 넣어줌
        if jsMatch == 0:
            totalDic = {}
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
            totalDic['matching'] = "N"
            totalList.append(totalDic)
    return totalList

# 리스트에 있는 것을 csv 형태의 파일로 출력
# input: top 전체 리스트
# output: 매칭된 결과 파일
def printTotal(list):
    csv_columns = list[2].keys()
    with open("C:/Users/이재원/Documents/code/matchingFile3.csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in list:
            writer.writerow(data)

def inputValueFormal(totalDic, jsDic, xmlDic):
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
    totalDic['matching'] = "Y"
    return totalDic



# jsFileList = jsParserNew.search("C:/Users/이재원/Documents/fsCode/FI_TOP_1Q-feature")
#
# jsList = jsParserNew.readJsFile(jsFileList)
#
# xmlFileList = xmlParser.search("C:/Users/이재원/Documents/fsCode/FI_TOP_1Q-feature")
# xmlList = xmlParser.readTlfFile(xmlFileList)


kk = matchXmlAndJs(xmlList, jsList)
printTotal(kk)
