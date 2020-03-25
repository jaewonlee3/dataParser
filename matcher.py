import xmlParser
import jsParser
import pprint

fileList = []
allFileList = jsParser.search("/Users/이재원/Documents/fs", fileList)

allList = jsParser.readJsFile(allFileList)

def matchXmlAndJs(xmlList, jsList):
    totalList = []

    return totalList