import os
from lxml import etree
from io import StringIO
from pprint import pprint
import csv
import utilFunc

# namespace 설정
ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
      'resource': 'http://www.tmaxsoft.com/top/SNAPSHOT/resource'}


# input: xml 트리의 노드
# output: 현재 노드의 총 뎁스
# Node의 Depth 구하는 함수, getParent 활용
def depth(node):
    d = 0
    while node is not None:
        d += 1
        node = node.getparent();
    return d

# input: xml 트리의 노드
# output: 노드가 속해있는 레이아웃
# Event가 어느 Layout에 속해있는지를 알려주는 함수, get parent 활용

def parentLayout(node, depth):
    while node.tag != "{http://www.tmaxsoft.com/top/SNAPSHOT/resource}LinearLayout":
        depth -= 1
        node = node.getparent();
    return node, depth

# input: xml 트리의 노드
# output: 해당 노드가 있는 레이아웃의 WebController
# 해당 위젯이 있는 레이아웃의 WebController 찾기 -> Event가 지역 변수일경우 해당 webcontroller에 해당 Event가 존재
def findWebController(node):
    webController = None
    while node is not None:
        if webController is None:
            webController = node.get('webController')
        node = node.getparent();
    return webController

# input: xml 트리의 노드
# output: 해당 노드가 있는 레이아웃의 WebControllerJs
# 해당 위젯이 있는 레이아웃의 WebControllerJs 찾기
def findWebControllerJs(node):
    webController = None
    while node is not None:
        if webController is None:
            webController = node.get('webControllerJs')
        node = node.getparent();
    return webController

# # 모든 부모 Layout 찾기
# def allParentLayout(node):
#     parentLayoutList = []
#     while node is not None:
#         node = node.getparent();
#         if node is not None:
#             if node.tag == "{http://www.tmaxsoft.com/top/SNAPSHOT/resource}LinearLayout":
#                 parentLayoutList.append(node.get("id"))
#     return parentLayoutList

# input: xml 트리의 노드
# output: 해당 노드의 상위 위젯, 레이아웃을 리스트 형태로 표현
# 모든 부모 위젯 찾기
def allParentObject(node):
    parentList = []
    while node is not None:
        node = node.getparent();
        if node is not None:
            if (node.get('id') != None):
                parentList.append(node.get("id"))
    return parentList

# input: xml 트리의 노드
# ouput: 해당 노드의 바로 위 위젯
# 바로 위 위젯 찾기
def parentObject(node):
    node = node.getparent();
    parentObject = ""
    if node is not None:
        parentObject = node.get('id')
    return parentObject;

# input: 파일의 위치 텍스트
# output: 모든 event와 event에 관한 정보를 담은 리스트
# Event들 다 찾기
def findAllEvent(path):
    # Event를 담을 리스트
    listEvent = []
    # path 텍스트를 가져와서 각 depth를 리스트화
    pathList = utilFunc.findPath(path)
    # etree를 이용하여 xml 파일을 tree 구조로 변환
    tree = etree.parse(path)
    root = tree.getroot()
    # 해당 노드가 이벤트인지를 알려주는 키
    keyList = ['onClick', 'onDoubleClick', 'onKeyPressed', 'onUpdate', 'onSelect', 'onChange', 'onRowClick', 'onRowDoubleClick', 'onFoucs', 'onFocusLost', 'onKeyTyped', 'onAttach', 'onClose','onTabChange','onTabClick','onItemClick','onItemDoubleClick']
    for child in root.findall(".//resource:Event", ns):
        # Event들 정보 담을 Dictionary 생성
        innerList = {}
        # Event의 상위 위젯 id 및 Tag, Depth 찾아 담기
        childParent = child.getparent();
        innerList['widgetId'] = childParent.get('id')
        # 노드가 keyList의 key를 가지고 있으면, 해당 key를 활용해서 event의 id를 찾기
        value = child.get('onKeyReleased')
        for key in keyList:
            value = findEvent(value,key,child)
        innerList['eventId'] = value
        if value is not None:
            innerList['eventId'] = innerList['eventId'].replace("#","")
        # Event의 상위 Layout id 및 Depth 찾아 담기
        nodeLayout, layoutDepth = parentLayout(child, depth(child))
        innerList['layoutId'] = nodeLayout.get("id")
        # Event의 webController, webControllerJs, path 찾아 담기
        innerList['webController'] = findWebController(child)
        innerList['webControllerJs'] = findWebControllerJs(child)
        innerList['path'] = pathList

        # Event 정보를 담은 Dictionary를 List에 추가
        listEvent.append(innerList)
    return listEvent

# # LinearLayout들 다 찾기
# def findAllLayout(path):
#     listLayout = []
#     pathList = findPath(path)
#     tree = etree.parse(path)
#     root = tree.getroot()
#     for child in root.findall(".//resource:LinearLayout", ns):
#         # LinearLayout 정보 담을 Dictionary 생성
#         innerList = {}
#         # LinearLayout id 및 Depth 찾아 담기
#         innerList['layoutId'] = child.get('id')
#         innerList['parentLayout'] = child.getparent().get("id");
#         innerList['allParentLayout'] = allParentLayout(child)
#         controlName = findWebController(child)
#         innerList['webController'] = controlName
#         controlNameJs = findWebControllerJs(child)
#         innerList['webControllerJs'] = controlNameJs
#         innerList['path'] = pathList
#         # LinearLayout 정보를 담은 Dictionary를 List에 추가
#         listLayout.append(innerList)
#     return listLayout

# input: 파일의 위치 텍스트
# output: tlf 파일에 있는 모든 위젯 및 위젯에 관한 정보 리스트
# tlf 파일에 있는 모든 Widget 및 위젯에 관한 정보 리스트 찾기
def findAllWidget(path):
    # 위젯들을 담을 리스트
    listWidget = []
    # path 텍스트를 가져와서 각 depth를 리스트화
    pathList = utilFunc.findPath(path)
    # etree를 이용하여 xml 파일을 tree 구조로 변환
    tree = etree.parse(path)
    root = tree.getroot()
    # root 위젯에 관한 정보를 담을 딕셔너리를 만들고, 해당 위젯의 ID, path, 상위 위젯, webController, webControllerJs를 담고 이를 리스트에 추가
    rootList = {}
    rootList['widgetID'] = root.get('id')
    rootList['allParentObject'] = []
    rootList['parentObject'] = ""
    rootList['path'] = pathList
    rootList['webController'] = root.get('webController')
    rootList['webControllerJs'] = root.get('webControllerJs')
    listWidget.append(rootList)
    # root 위젯의 하위 노드를 모두 돌면서 관한 정보를 담을 딕셔너리를 만들고,
    # 해당 위젯의 ID, path, 상위 위젯, webController, webControllerJs를 담고 이를 리스트에 추가
    for child in root.iter():
        innerList = {}
        if (child.get('id') != None):
            innerList['widgetID'] = child.get('id')
            innerList['allParentObject'] = allParentObject(child)
            innerList['parentObject'] = parentObject(child)
            innerList['path'] = pathList
            innerList['webController'] = findWebController(child)
            innerList['webControllerJs'] = findWebControllerJs(child)
            listWidget.append(innerList)
    return listWidget

# input: 폴더 텍스트
# output: 폴더에 있는 모든 tlf파일
# 폴더에서 거기 하위폴더들에 있는 tlf파일을 다 찾아줌
def search(folder):
    tlfFileList = []
    for (path, dir, files) in os.walk(folder):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.tlf':
                tlfFileList.append("%s/%s" % (path, filename))
    return tlfFileList

# input: 파일의 위치 텍스트
# output: 위젯과 이벤트에 관련한 정보
# 파일 위치를 찾아와서 전체 리스트를 읽어옴
def findAll(path):
    # findAllWidget과 findAllEvent 함수를 이용하여 widget List와
    widgetList = findAllWidget(path)
    eventList = findAllEvent(path)
    # widget List와 event List를
    allList = matciWidgetEvent(widgetList, eventList)
    allList_noDump = utilFunc.remove_dupe_dicts(allList)
    return allList_noDump

# input: widget 리스트와 event 리스트
# output: tlf 파일에서 알고자 하는 모든 정보를 담은 리스트
# EventList와 Widget List를 매칭해서 tlf 리스트 생성
def matciWidgetEvent(widgetList, eventList):
    # 리스트 생성
    allList = []
    for wid in widgetList:
        widMatch = 0
        for ev in eventList:
            # widget의 widget Id와 event의 widget Id가 같으면, widget에 event 정보 추가하고 이를 담기
            if wid['widgetID'] == ev['widgetId']:
                widMatch = widMatch + 1
                wid['eventId'] = ev['eventId']
                allList.append(wid)
        # event가 하나도 없는 widget일 경우 그대로 담기
        if widMatch == 0:
            wid['eventId'] = ""
            allList.append(wid)
    return allList

# input: tlf 파일 리스트
# output: tlf 파일에 있는 모든 위젯 및 위젯에 관한 정보 리스트
# Tlf 파일리스트를 가져와서 거기에 있는 파일들 읽고 파서 결과물 출력
def readTlfFile(list):
    allList = []
    for file in list:
        listInFile = findAll(file)
        allList = allList + listInFile
    return allList

# input: 현재 event의 id값, key 리스트에 있는 key, 노드
# output: event의 id값
# 기존의 event의 id값이 없으면, 해당 key가 노드에 있는지를 확인하고 있으면 id 값을 갱신할 것
def findEvent(value, key, child):
    if value is None:
            value = child.get(key)
    if value == "":
            value = child.get(key)
    return value

# input: 리스트값
# output: 리스트 값을 나열한 csv 파일
# xml의 리스트 값을 csv 파일로 출력
def printTotal(list):
    listFile = open("C:/Users/이재원/Documents/code/tlfList.csv", "w")
    wr = csv.writer(listFile)
    rowNum = 1
    wr.writerow([1,'xmlPath','webControllerJs','webController','parentObject','widgetID','eventID'])
    for Dic in list:
        rowNum = rowNum + 1
        wr.writerow([rowNum,Dic['path'],Dic['webControllerJs'],Dic['webController'],Dic['parentObject'],Dic['widgetID'],Dic['eventId']])
#
# Event 및 Layout List 출력
#
# fileList = []

# totalList = search('C:/Users/이재원/Documents/FI_TOP_1Q-feature')
# allList = readTlfFile(totalList)
# printTotal(allList)