from flask import Flask
from flask import jsonify
from flask import request
import json
import PO_CONNECTOR
import TOP_CONNECTOR
import SOparser
import xmlParser
import jsParserNew
import matcher
import DBParser
import ERDParser
import poTopMatcher
import columnMatcher

app = Flask(__name__)

#TODO : Error 처리 추가 필요 #

@app.route("/POconnector", methods=['POST'])
def POconnector() :
    output = request.get_json()
    outputdto = output["dto"]
    AppName = outputdto["APPLICATION_NAME"]
    SgName = outputdto["SERVICEGROUP_NAME"]
    path = PO_CONNECTOR.POconnector(AppName, SgName)
    outputdto['SGpath'] = path
    #outputdto.append("2")
    return output

@app.route("/POparser", methods=['POST'])
def POparser() :
    output = request.get_json()
    outputdto = output["dto"]
    SGpath = outputdto["SGpath"]
    outputlist = SOparser.PoParser(SGpath)
    outputdto['SOlist'] = outputlist
    return output

@app.route("/TOPconnector", methods=['POST'])
def TOPconnector() :
    output = request.get_json()
    outputdto = output["dto"]
    AppName = outputdto["APPLICATION_NAME"]
    outputdto["TOP_PATH"]=TOP_CONNECTOR.TopXmlConnector(AppName)
    return output

@app.route("/TOPXMLparser", methods=['POST'])
def TOPXMLparser() :
    output = request.get_json()
    outputdto = output["dto"]
    path = outputdto["TOP_PATH"]
    fileList = []
    xmlFileList = xmlParser.search(path, fileList)
    xmlList = xmlParser.readTlfFile(xmlFileList)
    outputdto["XMLlist"] = xmlList
    return output

@app.route("/TOPJSparser", methods=['POST'])
def TOPJSparser() :
    output = request.get_json()
    outputdto = output["dto"]
    path = outputdto["TOP_PATH"]
    fileList = []
    jsFileList = jsParserNew.search(path)
    jsList = jsParserNew.readJsFile(jsFileList)
    outputdto["JSlist"] = jsList
    return output

@app.route("/XMLJSmatcher", methods=['POST'])
def XMLJSmatcher() :
    output = request.get_json()
    outputdto = output["dto"]
    xmlList = outputdto["XMLlist"]
    jsList = outputdto["JSlist"]
    toplist = matcher.matchXmlAndJs(xmlList, jsList)
    outputdto["TOPlist"] = toplist
    outputdto["XMLlist"] = ""
    outputdto["JSlist"] = ""
    return output

@app.route("/POTOPmatcher", methods=['POST'])
def POTOPmatcher() :
    output = request.get_json()
    outputdto = output["dto"]
    toplist = outputdto["TOPlist"]
    polist = outputdto["SOlist"]
    TOPPOlist = poTopMatcher.poTopMatchingDic(polist, toplist)
    outputdto["totalList"] = TOPPOlist
    outputdto["TOPlist"] = ""
    outputdto["SOlist"] = ""
    return output

@app.route("/DBconnector", methods=['POST'])
def DBconnector() :
    output = request.get_json()
    outputdto = output["dto"]
    ip = outputdto["IP"]
    user = outputdto["USER"]
    password = outputdto["PASSWORD"]
    outputdto["DBlist"] = DBParser.DBConn(ip, user, password)
    outputdto["USER"] = ""
    outputdto["PASSWORD"] = ""
    return output

@app.route("/DBparser", methods=['POST'])
def DBparser() :
    output = request.get_json()
    outputdto = output["dto"]
    rs = outputdto["DBlist"]
    outputlist = DBParser.DBParser(rs)
    outputdto["DBparsinglist"] = outputlist
    outputdto["DBlist"] = ""
    return output

@app.route("/ERDconnector", methods=['POST'])
def ERDconnector() :
    output = request.get_json()
    output["dto"]["file_dir"] = "Copy of Copy of PS_TIMS_cys.sql"
    return output

@app.route("/ERDparser", methods=['POST'])
def ERDparser() :
    output = request.get_json()
    outputdto = output["dto"]
    inputFile = outputdto["file_dir"]
    ERDlist = ERDParser.ERDparser(inputFile)
    outputdto["ERDlist"] = ERDlist
    return output

@app.route("/columnDBmatcher", methods=['POST'])
def columnDBmatcher() :
    output = request.get_json()
    outputdto = output["dto"]
    totallist = outputdto["totalList"]
    dblist = outputdto["DBparsinglist"]
    #erdlist = outputdto["ERDlist"]
    rs = columnMatcher.matchQueryandDB(totallist, dblist)
    outputdto["totallist"] = rs
    outputdto["DBparsinglist"] = ""
    #rs2 = columnMatcher.matchQueryandERD(rs, erdlist)
    return output

@app.route("/columnERDmatcher", methods=['POST'])
def columnERDmatcher() :
    output = request.get_json()
    outputdto = output["dto"]
    totalist = outputdto["totalList"]
    erdlist = outputdto["ERDlist"]
    rs = columnMatcher.matchQueryandERD(totalist, erdlist)
    outputdto["totallist"] = rs
    outputdto["ERDlist"] = ""
    return output

if __name__ == "__main__" :
    app.config["JSON_SORT_KEYS"]=False
    app.run(host='0.0.0.0')
