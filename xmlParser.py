import os
from lxml import etree
from io import StringIO
from pprint import pprint

# namespace 설정
ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
      'resource': 'http://www.tmaxsoft.com/top/SNAPSHOT/resource'}


# Path 찾아서 리스트 형태로 
def findPath(path):
    path2 = path.split('/')
    pathList = []
    for p in path2:
        path3 = p.split('\\')
        for i in path3:
            pathList.append(i)
    return pathList

# Node의 Depth 구하는 함수, getParent 활용
def depth(node):
    d = 0
    while node is not None:
        d += 1
        node = node.getparent();
    return d
# Event, Layout의 목록을 담을 List 생성




# Event가 어느 Layout에 속해있는지를 알려주는 함수, get parent 활용

def parentLayout(node, depth):
    while node.tag != "{http://www.tmaxsoft.com/top/SNAPSHOT/resource}LinearLayout":
        depth -= 1
        node = node.getparent();
    return node, depth

# WebController 찾기

def findWebController(node):
    webController = None
    while node is not None:
        if webController is None:
            webController = node.get('webController')
        node = node.getparent();
    return webController

def findWebControllerJs(node):
    webController = None
    while node is not None:
        if webController is None:
            webController = node.get('webControllerJs')
        node = node.getparent();
    return webController

# 모든 부모 Layout 찾기
def allParentLayout(node):
    parentLayoutList = []
    while node is not None:
        node = node.getparent();
        if node is not None:
            if node.tag == "{http://www.tmaxsoft.com/top/SNAPSHOT/resource}LinearLayout":
                parentLayoutList.append(node.get("id"))
    return parentLayoutList

# 모든 부모 위젯 찾기
def allParentObject(node):
    parentList = []
    while node is not None:
        node = node.getparent();
        if node is not None:
            if (node.get('id') != None):
                parentList.append(node.get("id"))
    return parentList

#바로 위 위젯 찾기
def parentObject(node):
    node = node.getparent();
    parentObject = ""
    if node is not None:
        parentObject = node.get('id')
    return parentObject;

# Event들 다 찾기
def findAllEvent(path):
    listEvent = []
    pathList = findPath(path)
    tree = etree.parse(path)
    root = tree.getroot()
    keyList = ['onClick', 'onDoubleClick', 'onKeyPressed', 'onUpdate', 'onSelect', 'onChange', 'onRowClick', 'onRowDoubleClick', 'onFoucs', 'onFocusLost', 'onKeyTyped', 'onAttach', 'onClose','onTabChange','onTabClick','onItemClick','onItemDoubleClick']
    for child in root.findall(".//resource:Event", ns):
        # Event들 정보 담을 Dictionary 생성
        innerList = {}
        # Event의 상위 위젯 id 및 Tag, Depth 찾아 담기
        childParent = child.getparent();
        innerList['widgetId'] = childParent.get('id')
        # Event의 Depth와 Key 찾아 담기
        value = child.get('onKeyReleased')
        for key in keyList:
            value = findEvent(value,key,child)
        innerList['eventId'] = value
        if value is not None:
            innerList['eventId'] = innerList['eventId'].replace("#","")
        # Event의 상위 Layout id 및 Depth 찾아 담기
        nodeLayout, layoutDepth = parentLayout(child, depth(child))
        innerList['layoutId'] = nodeLayout.get("id")
        # Event의 Controller 파일 찾기
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

# 모든 Widget들 찾기
def findAllWidget(path):
    listWidget = []
    pathList = findPath(path)
    tree = etree.parse(path)
    root = tree.getroot()
    rootList = {}
    rootList['widgetID'] = root.get('id')
    rootList['allParentObject'] = []
    rootList['parentObject'] = "parentObject(child)"
    rootList['path'] = pathList
    rootList['webController'] = root.get('webController')
    rootList['webControllerJs'] = root.get('webControllerJs')
    listWidget.append(rootList)
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

# 폴더에서 거기 하위폴더들에 있는 tlf파일을 다 찾아줌
def search(dirname,fileList):
    try:
        filenames = os.listdir(dirname)
        for filename in filenames:
            full_filename = os.path.join(dirname, filename)
            if os.path.isdir(full_filename):
                search(full_filename, fileList)
            else:
                ext = os.path.splitext(full_filename)[-1]
                if ext == '.tlf':
                    fileList.append(full_filename)
    except PermissionError:
        pass
    finally:
        return fileList

# 파일 위치를 찾아와서 전체 리스트를 읽어옴
def findAll(path):
    widgetList = findAllWidget(path)
    eventList = findAllEvent(path)
    allList = matciWidgetEvent(widgetList, eventList)
    for number, tlfDic in enumerate(allList):
        if 'eventId' not in  tlfDic.keys():
            tlfDic['eventId'] = ""
        allList[number] = tlfDic
    return allList

# EventList와 Widget List를 매칭해서 tlf 리스트 생성
def matciWidgetEvent(widgetList, eventList):
    allList = []
    for wid in widgetList:
        widMatch = 0
        for ev in eventList:
            if wid['widgetID'] == ev['widgetId']:
                widMatch = widMatch + 1
                wid['eventId'] = ev['eventId']
                allList.append(wid)
        if widMatch == 0:
            allList.append(wid)
    return allList

# Tlf 파일리스트를 가져와서 거기에 있는 파일들 읽고 파서 결과물 출력
def readTlfFile(list):
    allList = []
    for file in list:
        listInFile = findAll(file)
        allList = allList + listInFile
    return allList


def findEvent(value, key, child):
    if value is None:
            value = child.get(key)
    if value == "":
            value = child.get(key)
    return value

#Event 및 Layout List 출력

# fileList = []
#
# totalList = search('C:/Users/이재원/Documents/fsCode/FI_TOP_1Q-feature', fileList)
# allList = readTlfFile(totalList)
# pprint(allList)
