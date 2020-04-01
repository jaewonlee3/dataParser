import os
import csv
import xmlParser
import jsParser
import SO파싱
import matcher
import ast
import re
import jsParserNew
import pprint
import utilFunc



def findListFromFile(path):
    with open(path, 'r', encoding='UTF-8') as f:
        mylist = ast.literal_eval(f.read())
    return mylist

def findDicFromFile(path):
    with open(path, 'r', encoding="UTF-8") as inf:
        allRead = inf.read()
        dicList = []
        tokenNum = 0
        newData = ""
        for i in allRead:
            if i == '{':
                newData = ""
                tokenNum = tokenNum + 1
                newData = newData + i
            elif i == '}':
                tokenNum = tokenNum - 1
                newData = newData + i
                dicList.append(newData)
            else:
                newData = newData + i
        for num, value in enumerate(dicList):
            dicData = ast.literal_eval(value)
            dicList[num] = dicData
        return dicList






def poTopMatchingMain(poPath, topPath):
    totalList = []
    poOutputFile = open(poPath,'r')
    poOutput = poOutputFile.read()
    poList = SO파싱.QueryLists
    querys = SO파싱.Querys
    UserPath = SO파싱.input('servicegroup.xml 경로를 입력해 주세요 : ')
    SO파싱.PoParser(UserPath)


    jsFileList = jsParserNew.search(topPath)

    jsList = jsParserNew.readJsFile(jsFileList)

    tlfFileList = []

    xmlFileList = xmlParser.search(topPath)
    xmlList = xmlParser.readTlfFile(xmlFileList)

    topList = matcher.matchXmlAndJs(xmlList, jsList)

    totalList = poTopMatching(poList, topList)

    return totalList


def poTopMatching(poList, topList):
    totalList = []
    jsPathMaxLen = 0
    poPathMaxLen = 0
    xmlPathMaxLen = 0
    parentObjMaxLen = 0


    for poL in poList:
        soNum = -1
        soIndex = findSoIndex(poL, soNum)
        if poPathMaxLen < (soIndex-2):
            poPathMaxLen = soIndex-2
    for topL in topList:
        if xmlPathMaxLen < len(topL['xmlPath']):
            xmlPathMaxLen = len(topL['xmlPath'])
        if jsPathMaxLen < len(topL['jsPath']):
            jsPathMaxLen = len(topL['jsPath'])
        if parentObjMaxLen < len(topL['parentObject']):
            parentObjMaxLen = len(topL['parentObject'])

    for poL in poList:
        poMatch = 0
        soNum = -1
        soIndex = findSoIndex(poL, soNum)
        lenPoL = len(poL)
        # po에서 app은 0, sg는 1, 나머지 path는 2부터 soIndex-1까지, so는 soIndex, BO는 soIndex + 1, DOF는 soIndex + 3, Query는 soIndex + 5
        # 각각의 자리를 찾아보자
        # xmlPath 자리는 0부터 xmlPathMaxLen-1까지 parentWidget은 xmlPathMaxLen부터 xmlPathMaxLen + parentObjMaxLen - 1까지 widgetId는 xmlPathMaxLen + parentObjMaxLen까지
        # Controller는 xmlPathMaxLen + parentObjMaxLen + 1, EventID는 xmlPathMaxLen + parentObjMaxLen + 2, jsPath는 xmlPathmaxLen + parentObjMaxLen + 2부터 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 2까지
        # app은 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 3, sg는 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 4, so는 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 5
        # soPath는 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 6 부터 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 5까지 BO는 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 6
        # DOF는 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 7 Query는 xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 8
        for topL in topList:
            if topL['app'] == poL[0] and topL['sg'] == poL[1] and topL['so'] == exchangeSoName(poL, soIndex):
                nowList = ["" for i in range(0, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 10)]
                poMatch = poMatch + 1
                inputListToTotal(topL, 'xmlPath', nowList, 0, xmlPathMaxLen-1)
                inputListToTotal(topL, 'parentObject', nowList, xmlPathMaxLen, xmlPathMaxLen + parentObjMaxLen - 1)
                nowList[xmlPathMaxLen + parentObjMaxLen] = topL['widget']
                nowList[xmlPathMaxLen + parentObjMaxLen + 1] = topL['controller']
                nowList[xmlPathMaxLen + parentObjMaxLen + 2] = topL['event']
                inputListToTotal(topL, 'jsPath', nowList, xmlPathMaxLen + parentObjMaxLen + 3, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 2)
                nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 3] = topL['app']
                nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 4] = topL['sg']
                nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 5] = topL['so']
                inputPoListToTotal(poL, nowList, 2, soIndex-1, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 6, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 5)
                nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 6] = poL[soIndex + 1]
                nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 7] = poL[soIndex + 3]
                if lenPoL > soIndex + 5:
                    nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 8] = poL[soIndex + 5]
                if topL['matching'] == "Y":
                    nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 9] = "Y"
                else:
                    nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 9] = "N"
                totalList.append(nowList)
        if poMatch == 0:
            nowList = ["" for i in range(0,xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 10)]
            for i in range(0, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 3):
                nowList[i] = ""
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 3] = poL[0]
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 4] = poL[1]
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 5] = exchangeSoName(poL, soIndex)
            inputPoListToTotal(poL, nowList, 2, soIndex - 1, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 6, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 5)
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 6] = poL[soIndex + 1]
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 7] = poL[soIndex + 3]
            if lenPoL > soIndex + 5:
                nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 8] = poL[soIndex + 5]
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 9] = "N"
            totalList.append(nowList)

    for topL in topList:
        topMatch = 0
        for poL in poList:
            soNum = -1
            soIndex = findSoIndex(poL, soNum)
            if topL['app'] == poL[0] and topL['sg'] == poL[1] and topL['so'] == exchangeSoName(poL, soIndex):
                topMatch = topMatch + 1
        if topMatch == 0:
            nowList = ["" for i in range(0,xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 10)]
            inputListToTotal(topL, 'xmlPath', nowList, 0, xmlPathMaxLen - 1)
            inputListToTotal(topL, 'parentObject', nowList, xmlPathMaxLen, xmlPathMaxLen + parentObjMaxLen - 1)
            nowList[xmlPathMaxLen + parentObjMaxLen] = topL['widget']
            nowList[xmlPathMaxLen + parentObjMaxLen + 1] = topL['controller']
            nowList[xmlPathMaxLen + parentObjMaxLen + 2] = topL['event']
            inputListToTotal(topL, 'jsPath', nowList, xmlPathMaxLen + parentObjMaxLen + 3, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 2)
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 3] = topL['app']
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 4] = topL['sg']
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 5] = topL['so']
            nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 9] = "N"
            totalList.append(nowList)
    return totalList

def poTopMatchingDic(poList, topList):
    totalList = []
    jsPathMaxLen = 0
    poPathMaxLen = 0
    xmlPathMaxLen = 0
    parentObjMaxLen = 0


    for poL in poList:
        soNum = -1
        soIndex = findSoIndex(poL, soNum)
        if poPathMaxLen < (soIndex-2):
            poPathMaxLen = soIndex-2
    for topL in topList:
        if xmlPathMaxLen < len(topL['xmlPath']):
            xmlPathMaxLen = len(topL['xmlPath'])
        if jsPathMaxLen < len(topL['jsPath']):
            jsPathMaxLen = len(topL['jsPath'])
        if parentObjMaxLen < len(topL['parentObject']):
            parentObjMaxLen = len(topL['parentObject'])

    for poL in poList:
        poMatch = 0
        soNum = -1
        for topL in topList:
            if topL['app'] == poL['APPLICATION_NAME'] and topL['sg'] == poL['SERVICEGROUP_NAME'] and topL['so'] == exchangeSoName(poL):
                nowDic = {}
                poMatch = poMatch + 1
                inputListToDic(topL, 'xmlPath', nowDic, 'XML_PATH_DEPTH', xmlPathMaxLen)
                inputListToDic(topL, 'parentObject', nowDic, 'PARENT_OBJECT_DEPTH', parentObjMaxLen)
                nowDic['WIDGET_NAME'] = topL['widget']
                nowDic['CONTROLLER_NAME'] = topL['controller']
                nowDic['EVENT_NAME'] = topL['event']
                inputListToDic(topL, 'jsPath', nowDic, 'JS_PATH_DEPTH', jsPathMaxLen)
                nowDic['APPLICATION_NAME'] = topL['app']
                nowDic['SERVICEGROUP_NAME'] = topL['sg']
                nowDic['SO_NAME'] = topL['so']
                nowDic['META'] = poL['META']
                for i in range(0,6):
                    if 'DEPTH ' + str(i) in poL.keys():
                        nowDic['DEPTH ' + str(i)] = poL['DEPTH ' + str(i)]
                inputPoValue(poL, 'BO_NAME', nowDic, 'BO_NAME')
                inputPoValue(poL, 'METHOD_NAME', nowDic, 'METHOD_NAME')
                inputPoValue(poL, 'DOF_NAME', nowDic, 'DOF_NAME')
                inputPoValue(poL, 'QUERY_NAME', nowDic, 'QUERY_NAME')
                inputPoValue(poL, 'QUERY', nowDic, 'QUERY')
                inputPoValue(poL, 'SCHEMA', nowDic, 'SCHEMA')
                inputPoValue(poL, 'TABLE', nowDic, 'TABLE')
                inputPoValue(poL, 'COLUMN', nowDic, 'COLUMN')
                nowDic['TOP_MATCHING'] = topL['matching']
                nowDic['TOP_PO_MATCHING'] = "Y"
                totalList.append(nowDic)
        if poMatch == 0:
            nowDic = {}
            inputBlankToDic(nowDic, 'XML_PATH_DEPTH', xmlPathMaxLen)
            inputBlankToDic(nowDic, 'PARENT_OBJECT_DEPTH', parentObjMaxLen)
            nowDic['WIDGET_NAME'] = ""
            nowDic['CONTROLLER_NAME'] = ""
            nowDic['EVENT_NAME'] = ""
            inputBlankToDic(nowDic, 'JS_PATH_DEPTH', jsPathMaxLen)
            nowDic['APPLICATION_NAME'] = poL['APPLICATION_NAME']
            nowDic['SERVICEGROUP_NAME'] = poL['SERVICEGROUP_NAME']
            nowDic['SO_NAME'] = poL['SO_NAME']
            nowDic['META'] = poL['META']
            for i in range(0, 6):
                if 'DEPTH ' + str(i) in poL.keys():
                    nowDic['DEPTH ' + str(i)] = poL['DEPTH ' + str(i)]
            inputPoValue(poL,'BO_NAME', nowDic, 'BO_NAME')
            inputPoValue(poL, 'METHOD_NAME', nowDic, 'METHOD_NAME')
            inputPoValue(poL, 'DOF_NAME', nowDic, 'DOF_NAME')
            inputPoValue(poL, 'QUERY_NAME', nowDic, 'QUERY_NAME')
            inputPoValue(poL, 'QUERY', nowDic, 'QUERY')
            inputPoValue(poL, 'SCHEMA', nowDic, 'SCHEMA')
            inputPoValue(poL, 'TABLE', nowDic, 'TABLE')
            inputPoValue(poL, 'COLUMN', nowDic, 'COLUMN')
            nowDic['TOP_MATCHING'] = "N"
            nowDic['TOP_PO_MATCHING'] = "N"
            totalList.append(nowDic)

    for topL in topList:
        topMatch = 0
        for poL in poList:
            soNum = -1
            soIndex = findSoIndex(poL, soNum)
            if topL['app'] == poL['APPLICATION_NAME'] and topL['sg'] == poL['SERVICEGROUP_NAME'] and topL['so'] == exchangeSoName(poL):
                topMatch = topMatch + 1
        if topMatch == 0:
            nowDic = {}
            inputListToDic(topL, 'xmlPath', nowDic, 'XML_PATH_DEPTH', xmlPathMaxLen)
            inputListToDic(topL, 'parentObject', nowDic, 'PARENT_OBJECT_DEPTH', parentObjMaxLen)
            nowDic['WIDGET_NAME'] = topL['widget']
            nowDic['CONTROLLER_NAME'] = topL['controller']
            nowDic['EVENT_NAME'] = topL['event']
            inputListToDic(topL, 'jsPath', nowDic, 'JS_PATH_DEPTH', jsPathMaxLen)
            nowDic['APPLICATION_NAME'] = topL['app']
            nowDic['SERVICEGROUP_NAME'] = topL['sg']
            nowDic['SO_NAME'] = topL['so']
            nowDic['META'] = ""
            for i in range(0, 6):
                nowDic['DEPTH ' + str(i)] = ""
            nowDic['BO_NAME'] = ""
            nowDic['METHOD_NAME'] = ""
            nowDic['DOF_NAME'] = ""
            nowDic['QUERY_NAME'] = ""
            nowDic['QUERY'] = ""
            nowDic['SCHEMA'] = ""
            nowDic['TABLE'] = ""
            nowDic['COLUMN'] = ""
            nowDic['TOP_MATCHING'] = topL['matching']
            nowDic['TOP_PO_MATCHING'] = "N"
            totalList.append(nowDic)
    return totalList

def inputPoValue(list, value, totalDic, key):
    if value in list.keys():
        totalDic[key] = list[value]
    else:
        totalDic[key] = ""

def inputListToDic(list, value, totalDic, key, maxLen):
    for i in range(1, maxLen+1):
        if i < len(list[value]):
            totalDic[key + str(i)] = list[value][i-1]
        else:
            totalDic[key + str(i)] = ""

def inputBlankToDic(totalDic, key, maxLen):
    for i in range(1, maxLen+1):
        totalDic[key + str(i)] = ""


def inputListToTotal(list, value, totalList, startIndex, lastIndex):
    lenList = len(list)
    for num, val in enumerate(list[value]):
        totalList[startIndex + num] = val


def inputPoListToTotal(list, totalList, startNum, lastNum, startIndex, lastIndex):
    for num, val in enumerate(list[startNum: lastNum+1]):
        totalList[startIndex + num] = val

def exchangeSoName(poL):
    soName = poL['SO_NAME']
    lenSo = len(soName)
    if soName[lenSo-1] != "O" or soName[lenSo-2] != "S":
        soName = soName + "S" + "O"
    return soName

def findSoIndex(poL, soIndex):
    for num, val in enumerate(poL):
        soFind = val.find("SO_NAME")
        if soFind > -1:
            soIndex = num
    return soIndex

def printTotal(list):
    listFile = open("C:/Users/이재원/Documents/code/poTopMatchingFile3.csv", "w")
    wr = csv.writer(listFile)
    rowNum = 0
    for l in list:
        rowNum = rowNum + 1
        inputList = []
        inputList.append(rowNum)
        for i in l:
            inputList.append(i)
        wr.writerow(inputList)
    listFile.close()

def printTotalDic(list):
    csv_columns = list[2].keys()
    with open("C:/Users/이재원/Documents/code/poTopMatchingDic.csv", 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in list:
            writer.writerow(data)


# jsFileList = jsParserNew.search("C:/Users/이재원/Documents/FI_TOP_1Q-feature")
# jsList = jsParserNew.readJsFile(jsFileList)
#
#
# xmlFileList = xmlParser.search("C:/Users/이재원/Documents/FI_TOP_1Q-feature")
# xmlList = xmlParser.readTlfFile(xmlFileList)
#
# topList = matcher.matchXmlAndJs(xmlList, jsList)
#
# poList = findDicFromFile('C:/Users/이재원/Documents/code/Sodict.txt')
#
# totalList = poTopMatchingDic(poList, topList)
#
# printTotalDic(totalList)
