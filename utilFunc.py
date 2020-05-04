import re
import json
import os


# 주석 제거
# input: 자바스크립트 텍스트
# output: 자바스크립트 텍스트
# 현재까지 진행한 주석 제거 작업: //로 시작하는 스크립트 라인들 모두 제거
# /*과 */ 사이에 있는 스크립트 모두 제거
# ""와 ''사이에 있을 경우 //나 /*이 있어도 주석으로 인식 안하게 함
def delAnnotation(allLine):
    allLine = allLine.replace('\t', '')
    newData = ""
    annoNum = 0
    # 상태가 0일 경우: 주석으로 인식하지 않고 일반 스크립트로 인식
    # 상태가 1일 경우: *이나 /가 나올 시 주석으로 인식할 상황
    # 상태가 2일 경우: 주석으로 인식 엔터가 나오면 주석으로 더이상 인식하지 않음
    # 상태가 3, 4일 경우: //나 /*이 나와도 주석으로 인식하지 않음
    # 상태가 5일 경우: 엔터가 쳐져도 주석으로 인식
    # 상태가 6일 경우:
    for i in allLine:
        # 엔터가 눌러지면, /*, */ 안에 있는 경우가 아니면 상황 초기화
        if i == '\n':
            if annoNum < 5:
                annoNum = 0
        # /로 시작하면 /가 나오거나 *이 나올 시 주석으로 인식할 수 있는 상황으로 인식
        if i == '/' and annoNum == 0:
            annoNum = 1
        # //가 되면 주석으로 인식
        elif i == '/' and annoNum == 1:
            annoNum = 2
        # "와 ' 사이에 있는 경우에는 주석이 작동하지 않는 특별 상태로 인식
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
        # *나 /가 아닐경우 원래 상태로 돌아옴
        elif annoNum == 1 and i != '*':
            newData = newData + '/'
            newData = newData + i
            annoNum = 0
        # 주석 상태에서는 텍스트를 추가하지 않음
        elif annoNum == 2:
            newData = newData
        # /*가 되면 주석 상태로 변함
        elif annoNum == 1 and i == '*':
            annoNum = 5
        # /* 주석 상태에서 *가 나오면 바로 다음 /가 나올 시 주석을 풀 수 있는 상태로 변환
        elif annoNum == 5 and i == '*':
            annoNum = 6
        elif annoNum == 6 and i == '*':
            annoNum = 6
        # */가 되면 주석을 풀고 아닐 경우 다시 주석 상태로 변환
        elif i == '/' and annoNum == 6:
            annoNum = 0
        # */가 아닐 경우 주석으로 인식
        elif annoNum == 6 and i != '*':
            annoNum = 5
        elif annoNum == 5:
            newData = newData
        # 이외의 상황에서는 텍스트 추가
        else:
            newData = newData + i
    return newData


# input: 겹치는게 있는 리스트
# output: 중복되는 값이 없느 리스트
# 겹치는 리스트들을 제거해줌
def remove_dupe_dicts(l):
  list_of_strings = [json.dumps(d, sort_keys=True) for d in l]
  list_of_strings = set(list_of_strings)
  return [json.loads(s)for s in list_of_strings]


# input: 파일의 위치 텍스트
# output: Path를 리스트 형태로 나타낸 것
# 파일 위치를 받아서 전체 Path들을 리스트화해줌
def findPath(path):
    path2 = path.split('/')
    pathList = []
    for p in path2:
        path3 = p.split('\\')
        for i in path3:
            pathList.append(i)
    return pathList

# input: javascript 텍스트와 해당 텍스트 중 어디부터 읽을지 알려주는 스타트 포인트
# output: 특정 function 혹은 controller 안에 있는 텍스트
# function과 controller 안에 있는 텍스트들을 찾음
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


# input:
# output:
#
def inputListToDic(list, value, totalDic, key, maxLen):
    for i in range(1, maxLen+1):
        if i < len(list[value]):
            totalDic[key + str(i)] = list[value][i-1]
        else:
            totalDic[key + str(i)] = ""


# input: 폴더 텍스트, 확장자
# output: 폴더에 있는 모든 tlf파일
# 폴더에서 거기 하위폴더들에 있는 tlf파일을 다 찾아줌
def search(folder, extension):
    fileList = []
    for (path, dir, files) in os.walk(folder):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == extension:
                fileList.append("%s/%s" % (path, filename))
    return fileList