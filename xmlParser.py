from lxml import etree
from io import StringIO

ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
      'resource': 'http://www.tmaxsoft.com/top/SNAPSHOT/resource'}

tree = etree.parse("/Users/이재원/Documents/code/a.xml")
root = tree.getroot()

def depth(node):
    d = 0
    while node is not None:
        d += 1
        node = node.getparent();
    return d

listEvent = []
listLayout = []

for child in root.findall(".//resource:Event", ns):
    innerList = []
    innerList.append(depth(child))
    print(depth(child))
    value = child.get('onKeyReleased')
    if value is None:
        value = child.get('onClick')
    innerList.append(value)
    print(value)
    childParent = child.getparent();
    print(depth(childParent))
    innerList.append(depth(childParent))
    print(childParent.tag)
    innerList.append(childParent.tag)
    innerList.append(childParent.get("id"))
    print(childParent.get("id"))
    listEvent.append(innerList)


for child in root.findall(".//resource:LinearLayout", ns):
    print(depth(child))
    value2 = child.get('id')
    print(value2)


print(listEvent[1][3])
