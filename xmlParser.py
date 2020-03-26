from lxml import etree
from io import StringIO
from pprint import pprint

# namespace 설정
ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
      'resource': 'http://www.tmaxsoft.com/top/SNAPSHOT/resource'}

# xml 트리 형태로 만들기

tree = etree.parse("/Users/이재원/Documents/code/contractListLayout.xml")
root = tree.getroot()

def findPath(path):
    path2 = path.split('/')
    pathList = []
    for i in path2:
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
    for child in root.findall(".//resource:Event", ns):
        # Event들 정보 담을 Dictionary 생성
        innerList = {}
        # Event의 Depth와 Key 찾아 담기
        value = child.get('onKeyReleased')
        if value is None:
            value = child.get('onClick')
        innerList['eventId'] = value
        # Event의 상위 위젯 id 및 Tag, Depth 찾아 담기
        childParent = child.getparent();
        innerList['widgetTag'] = childParent.tag
        innerList['widgetId'] = childParent.get('id')
        # Event의 상위 Layout id 및 Depth 찾아 담기
        nodeLayout, layoutDepth = parentLayout(child, depth(child))
        innerList['layoutId'] = nodeLayout.get("id")
        # Event의 Controller 파일 찾기
        controlName = findWebController(child)
        innerList['webController'] = controlName
        innerList['path'] = pathList

        # Event 정보를 담은 Dictionary를 List에 추가
        listEvent.append(innerList)
    return listEvent

# LinearLayout들 다 찾기
def findAllLayout(path):
    listLayout = []
    pathList = findPath(path)
    tree = etree.parse(path)
    root = tree.getroot()
    for child in root.findall(".//resource:LinearLayout", ns):
        # LinearLayout 정보 담을 Dictionary 생성
        innerList = {}
        # LinearLayout id 및 Depth 찾아 담기
        innerList['layoutId'] = child.get('id')
        innerList['parentLayout'] = child.getparent().get("id");
        innerList['allParentLayout'] = allParentLayout(child)
        controlName = findWebController(child)
        innerList['webController'] = controlName
        innerList['path'] = pathList
        # LinearLayout 정보를 담은 Dictionary를 List에 추가
        listLayout.append(innerList)
    return listLayout

def findAllWidget(path):
    listWidget = []
    pathList = findPath(path)
    tree = etree.parse(path)
    root = tree.getroot()
    for child in root.iter():
        innerList = {}
        if (child.get('id') != None):
            innerList['widgetID'] = child.get('id')
            innerList['allParentObject'] = allParentObject(child)
            innerList['parentObject'] = parentObject(child)
            innerList['path'] = pathList
            listWidget.append(innerList)
    return listWidget




#Event 및 Layout List 출력
pprint(findAllEvent("/Users/이재원/Documents/code/a.xml"))
pprint(findAllLayout("/Users/이재원/Documents/code/a.xml"))
pprint(findAllWidget("/Users/이재원/Documents/code/a.xml"))
