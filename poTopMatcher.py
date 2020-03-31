import os
import csv
import xmlParser
import jsParser
import SO파싱
import matcher
import ast
import re



def findListFromFile(path):
    with open(path, 'r', encoding='UTF-8') as f:
        mylist = ast.literal_eval(f.read())
    return mylist






def poTopMatchingMain(poPath, topPath):
    totalList = []
    poOutputFile = open(poPath,'r')
    poOutput = poOutputFile.read()
    poList = SO파싱.QueryLists
    querys = SO파싱.Querys
    UserPath = SO파싱.input('servicegroup.xml 경로를 입력해 주세요 : ')
    SO파싱.PoParser(UserPath)

    fileList = []
    jsFileList = jsParser.search(topPath, fileList)

    jsList = jsParser.readJsFile(jsFileList)

    tlfFileList = []

    xmlFileList = xmlParser.search("C:/Users/이재원/Documents/fsCode/FI_TOP_1Q-feature", tlfFileList)
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

    print(poPathMaxLen)
    print(xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 8)
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
                nowList[xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 9] = "Y"
                totalList.append(nowList)
        if poMatch == 0:
            nowList = ["" for i in range(0,xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + poPathMaxLen + 10)]
            for i in range(0, xmlPathMaxLen + parentObjMaxLen + jsPathMaxLen + 2):
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

def inputListToTotal(list, value, totalList, startIndex, lastIndex):
    lenList = len(list)
    for num, val in enumerate(list[value]):
        totalList[startIndex + num] = val


def inputPoListToTotal(list, totalList, startNum, lastNum, startIndex, lastIndex):
    for num, val in enumerate(list[startNum: lastNum+1]):
        totalList[startIndex + num] = val

def exchangeSoName(poL, soIndex):
    soVal = poL[soIndex]
    soCompile = re.compile('SO[_]NAME\s?:\s?')
    soLast = soCompile.search(soVal).end()
    soName = soVal[soLast:]
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

fileList = []
jsFileList = jsParser.search("C:/Users/이재원/Documents/FI_TOP_1Q-feature", fileList)

jsList = jsParser.readJsFile(jsFileList, "C:/Users/이재원/Documents/FI_TOP_1Q-feature")

tlfFileList = []

xmlFileList = xmlParser.search("C:/Users/이재원/Documents/FI_TOP_1Q-feature", tlfFileList)
xmlList = xmlParser.readTlfFile(xmlFileList)

topList = matcher.matchXmlAndJs(xmlList, jsList)

poList = findListFromFile('C:/Users/이재원/Documents/code/PoParserOutput.txt')

totalList = poTopMatching(poList, topList)

printTotal(totalList)
