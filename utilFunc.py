import re
import json


# 주석 제거
# input: 자바스크립트 텍스트
# output: 자바스크립트 텍스트
# 현재까지 진행한 주석 제거 작업: //로 시작하는 스크립트 라인들 모두 제거
# /*과 */ 사이에 있는 스크립트 모두 제거
# ""와 ''사이에 있을 경우 //나 /*이 있어도 주석으로 인식 안하게 함
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
            annoNum = 6
        elif i == '/' and annoNum == 6:
            annoNum = 0
        elif annoNum == 6 and i != '*':
            annoNum = 5
        elif annoNum == 5:
            newData = newData
        else:
            newData = newData + i

    return newData

# 겹치는 리스트들을 제거해줌
def remove_dupe_dicts(l):
  list_of_strings = [json.dumps(d, sort_keys=True) for d in l]
  list_of_strings = set(list_of_strings)
  return [json.loads(s)for s in list_of_strings]

# 파일 위치를 받아서 전체 Path들을 리스트화해줌
def findPath(path):
    path2 = path.split('/')
    pathList = []
    for p in path2:
        path3 = p.split('\\')
        for i in path3:
            pathList.append(i)
    return pathList

def collectInnerScript(data, startPoint):
    tokenNum = 0
    newData = ""
    for i in data[startPoint:]:
        if i == '{':
            tokenNum = tokenNum + 1
            newData = newData + i
        elif i == '}':
            tokenNum = tokenNum - 1
            newData = newData + i
        else:
            newData = newData + i
        if tokenNum == 0:
            break
    return newData