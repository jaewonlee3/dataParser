import xml.etree.ElementTree as elemTree
import re
import copy
import os
import sys
from sqlParser import RecursiveTokenParser

#Query를 저장하기 위한 list,
# 각각의 원소는 [APP,SG, meta, com, tmax, ...depths, so, SoName, BoName, MethodName, DofName, QueryAliasName, Query] 로 구성된다.
# string 파싱용
# 개발자가 BO에 query문을 실행할 때, 버츄얼모듈이나, aftercode에 직접 손코딩을 할 수도 있다.
# 이부분은 손코딩한 부분을 string으로 전부 가져와 setQuery 함수를 실행한 부분을 파싱해온다.
getSetQuery = re.compile("setFullQuery[(]\S+|setDynamicQuery[(]\S+|setUserQuery[(]\S+")
getAlias = re.compile("QUERY[.]\w+")

# xml 파일 내부의 각종 depth에 접근하기 위한 변수들
# 현재는 .so, .bo 등등 자동으로 generate 되므로 아래의 변수들은 변하지 않는다고 가정한다.
# 하지만 변한다면 파일 내에서 parsing 해오는 식으로 바꿔야 할 수도 있다.
SoVariable = '{http://www.tmax.co.kr/proobject/serviceobject}variable'
userDefined = '{http://www.tmax.co.kr/proobject/flow}userDefined'
bizMethodCall = '{http://www.tmax.co.kr/proobject/flow}bizMethodCall'
bizInstanceInfo = '{http://www.tmax.co.kr/proobject/flow}bizInstanceInfo'
bizClassInfo = '{http://www.tmax.co.kr/proobject/flow}bizInstanceInfo/{http://www.tmax.co.kr/proobject/flow}classInfo'
bizMethod = '{http://www.tmax.co.kr/proobject/bizobject}bizMethod'
BoMethods = '{http://www.tmax.co.kr/proobject/flow}method'
BoVirtualModule = '{http://www.tmax.co.kr/proobject/flow}virtualModule'
BoCode = '{http://www.tmax.co.kr/proobject/flow}code'
DofFullstatements = '{http://www.tmax.co.kr/proobject/dataobjectfactory}fullstatements'
DofDynamicstatements = '{http://www.tmax.co.kr/proobject/dataobjectfactory}dynamicstatements'
DofStatement = '{http://www.tmax.co.kr/proobject/dataobjectfactory}statement'

def SetQueryParser(SetQuery, QueryDict3, Metapath, doCall, QueryLists) :
    SetQuery = SetQuery.replace("setFullQuery(","").replace("setDynamicQuery(","").replace("setUserQuery(","")
    SetQuery = SetQuery.replace(");","")
    QueryInf = SetQuery.split("QUERY.")
    QueryInf[0] = QueryInf[0].replace(".FULL","")
    QueryInf[0] = QueryInf[0].replace(".DYNAMIC","")
    QueryInf[0] = QueryInf[0].replace(".USER","")
    DofPathInfs = QueryInf[0].split(".")
    if (len(DofPathInfs) >= 2) :
        DofInfoList = QueryInf[0].split(".")
        DofInfoList[len(DofInfoList)-1] = DofInfoList[len(DofInfoList)-1] + ".factory"
        DofInfoPath = DofInfoList[0]
        for i in range(len(DofInfoList)-1) :
            DofInfoPath = os.path.join(DofInfoPath,DofInfoList[i+1])
        DofPath = os.path.join(Metapath, DofInfoPath)
        #DofPath = Metapath + "/" + QueryInf[0].replace(".","/") + ".factory"
    else :
        DofName = DofPathInfs[len(DofPathInfs)-1]
        for classinfo in doCall.iter('{http://www.tmax.co.kr/proobject/flow}classInfo') :
            if (classinfo.get("className") == DofName) :
                DofPathInf = classinfo.get("classPackageName")
                break
        DofPathInf = DofPathInf + "." + DofName
        DofPathInfList = DofPathInf.split(".")
        DofPathInfList[len(DofPathInfList)-1] = DofPathInfList[len(DofPathInfList)-1] + ".factory"
        DofInfPath = DofPathInfList[0]
        for i in range(len(DofPathInfList)-1) :
            DofInfPath = os.path.join(DofInfPath, DofPathInfList[i+1])
        DofPath = os.path.join(Metapath, DofInfPath)
        #DofPath = Metapath + "/" + DofPathInf.replace(".","/") +"/" + DofName + ".factory"
    AliasName = QueryInf[1]
    # DOF 경로를 토대로 DOF 파일 파싱
    QueryDict4 = copy.deepcopy(QueryDict3)
    if (os.path.isfile(DofPath) != True) :
        QueryDict4["ERROR"] = "PARSING_SERVER_ERROR : Dof경로 에러.사용하지않는 DOF 이거나 빌드가 안된 DOF 이므로 영향도 분석에서 제외하겠습니다."
        QueryLists.append(QueryDict4)
        return 0
    DOFtree = elemTree.parse(DofPath)
    DOFroot = DOFtree.getroot()

    # DOF이름, DOF에서 호출될 쿼리 alias이름을 list에 담는다.
    QueryDict4["DOF_NAME"] = DOFroot.get("logicalName")
    QueryDict4["QUERY_NAME"] = AliasName
    QueryExtractor(QueryDict4, DOFtree, AliasName, DofFullstatements, QueryLists)
    QueryExtractor(QueryDict4, DOFtree, AliasName, DofDynamicstatements, QueryLists)
    return 0

def QueryExtractor(QueryDict4, DOFtree, AliasName, StatementType, QueryLists) :
    for statements in DOFtree.iter(StatementType) :
        if (statements.get('alias') == AliasName) :
            Query = statements.find(DofStatement).text
            processedQuery = Query.replace('\n', ' ')
            columnList = RecursiveTokenParser(processedQuery).extractColumn()
            QueryDict4["QUERY"] = processedQuery
            if (columnList == None) :
                QueryLists.append(QueryDict4)
                break
            else :
                if (len(columnList) == 0) :
                    QueryLists.append(QueryDict4)
                    break
                for column in columnList :
                    QueryDict5 = copy.deepcopy(QueryDict4)
                    if (len(column) == 0) :
                        QueryLists.append(QueryDict5)
                    else :
                        if (len(column) >= 1) :
                            QueryDict5["SCHEMA"] = column[0]
                        if (len(column) >= 2) :
                            QueryDict5["TABLE"] = column[1]
                        if (len(column) == 3) :
                            QueryDict5["COLUMN"] = column[2]
                        QueryLists.append(QueryDict5)
                break
    return 0

def PoParser(SGpath) :
    QueryLists = []
    #SGpath = '/data/git/FS/CORE/META-INF/servicegroup.xml'
    if (os.path.isfile(SGpath) != True) :
        error = {}
        error["ERROR"] = "PARSING_SERVER_ERROR : 잘못된 service group 경로 입니다. OS 별 directory 양식을 지켜주세요."
        QueryLists.append(error)
        return QueryLists
    SGtree = elemTree.parse(SGpath)
    SGroot = SGtree.getroot()

    # app이름, sg이름은 SG파일에 존재.
    # 위 2개를 이용하여 meta의 경로도 지정해 준다.
    AppName = SGroot.get("ApplicationName")
    SgName = SGroot.get("serviceGroupName")
    MetaInfPath = os.path.dirname(SGpath)
    MetaPathList = MetaInfPath.split(os.path.sep)
    if (len(MetaPathList) <= 1) :
        error = {}
        error["ERROR"] = "PARSING_SERVER_ERROR : 잘못된 service group 경로입니다. OS 별 directory 양식을 지켜주세요."
        QueryLists.append(error)
        return QueryLists
    if (MetaPathList[0] == "") :
        MetaPathList[0] = "/"
    MetaPathList.remove("META-INF")
    lastNum = len(MetaPathList)-1
    Metapath = os.path.join(MetaPathList[lastNum],"meta")
    for i in range(lastNum) :
        Metapath = os.path.join(MetaPathList[lastNum-1-i],Metapath)
    Metapath = Metapath.replace(":",":\\")
    if (os.path.isdir(Metapath) != True) :
        error = {}
        error["ERROR"] = "PARSING_SERVER_ERROR : 잘못된 meta 경로 입니다. \\대신 /를 사용해 주세요."
        QueryLists.append(error)
        return QueryLists

    # SG 내부의 SO 이름 및 경로들을 가져오기 위한 로직 시작.
    ns21 = SGroot.tag
    SOroot = ns21.replace('service-group','service-object')
    classname = ns21.replace('service-group','class-name')
    name = ns21.replace('service-group','name')

    for SO in SGroot.iter(SOroot) :
        # QueryLists에 담기위한 하나의 QueryDict 생성
        QueryDict = {}
        QueryDict["APPLICATION_NAME"] = AppName
        QueryDict["SERVICEGROUP_NAME"] = SgName
        QueryDict["META"] = "meta"

        # SO 파일에 도달하기 위한 디렉토리 파싱 (ex. com/tmax/infra...)
        SOclassname = SO.find(classname)
        directory = SOclassname.text.split(".")

        # directory-1을 하는 이유는 가장 마지막은 SO이름으로 되어있기 때문
        for i in range(len(directory)-1) :
            #print(directory[i])
            depth = "DEPTH " + str(i)
            QueryDict[depth] = directory[i]
        SOname = SO.find(name).text
        QueryDict["SO_NAME"] = SOname
        # SO파일 파싱
        SoclassnameList = SOclassname.text.split('.')
        SoclassnameList[len(SoclassnameList)-1] = SoclassnameList[len(SoclassnameList)-1] + ".so"
        Soclasspath = SoclassnameList[0]
        for i in range(len(SoclassnameList)-1) :
            Soclasspath = os.path.join(Soclasspath,SoclassnameList[i+1])

        SOpath = os.path.join(Metapath, Soclasspath)
        #SOpath = Metapath +"/"+ SOclassname.text.replace('.', '/') + '.so'

        if (os.path.isfile(SOpath) == False) :
            QueryDict["ERROR"] = "PARSING_SERVER_ERROR : 잘못된 SO 경로입니다. 사용하지 않거나 빌드가 제대로 되지않은 SO 이므로 영향도 분석에서 제외하겠습니다."
            QueryLists.append(QueryDict)
            continue

        tree = elemTree.parse(SOpath)
        root = tree.getroot()
        #print(QueryList)

    # SO 에서 bizMethodCall 에 의해 bo가 불린다.
    ##TODO 버츄얼 모듈을 통해 bo를 콜 할수도 있다. 이부분 추가 코딩 필요. ##
        for boCall in root.iter(bizMethodCall) :

            # bo가 여러개일 경우 위에서만든 QueryList 가 중복해서 여러개 필요하므로 깊은복사.
            QueryDict2 = copy.deepcopy(QueryDict)
        
            # bo 이름,경로가져오기.
            BoVariableName = boCall.find(bizInstanceInfo).get('variableName')
            for variable in root.iter(SoVariable) :
                if (variable.get('name') == BoVariableName) :
                    BoInf = variable.find(userDefined).text
                    break
            BoInfs = BoInf.split(".")
            BoName = BoInfs[len(BoInfs)-1]
            QueryDict2["BO_NAME"] = BoName
            BoInfs[len(BoInfs)-1] = BoInfs[len(BoInfs)-1] + '.bo'
            BoInfPath = BoInfs[0]
            for i in range(len(BoInfs)-1) :
                BoInfPath = os.path.join(BoInfPath, BoInfs[i+1])

            BOpath = os.path.join(Metapath, BoInfPath)

            if (os.path.isfile(BOpath) == False) :
                #print("잘못된 BO 경로입니다. 빌드를 확인해 주세요.")
                QueryDict2["ERROR"] = "PARSING_SERVER_ERROR : 잘못된 BO 경로입니다. 사용하지 않는 BO 이거나, 빌드가 되지 않은 BO 이므로 영향도 분석에서 제외하겠습니다."
                QueryLists.append(QueryDict2)
                continue
            #print(QueryList2)
       
            # bo 안의 메서드들 가져오기 (이 메서들마다 여러 쿼리가 존재할 수 있음, 쿼리는 dof로 부터 가져온다.).
            for method in boCall.findall(BoMethods) :
                QueryDict3 = copy.deepcopy(QueryDict2)
                MethodName = method.get('methodName')
                QueryDict3["METHOD_NAME"] = MethodName
                # BOpath로 bo 파일을 오픈하여, method 안에 담긴 퀴리문 가져오기 시작.
                #if (os.path.isfile(BOpath) == False) :
                #    QueryList3.append("BO path error")
                #    QueryLists.append(QueryList3)
                #    continue
                #else :
                BOtree = elemTree.parse(BOpath)
                BOroot = BOtree.getroot()
                #print(QueryList3)
            
                # 위에서 얻은 method 이름으로 bo 파일 내부의 method 정보를 찾는다.
                for BOmethod in BOroot.iter(bizMethod) :
                    if (BOmethod.get('methodName') == MethodName) :
                    
                        # 먼저 virtual module 안에 손으로 작성한 코드가 있는지 확인한다.
                        for virtualModule in BOmethod.iter(BoVirtualModule) :
                            if (virtualModule != None) :
                                code = virtualModule.find(BoCode).text
                                # 쿼리문은 setQuery 함수로 호출한다. (ex. setFullQuery, setDynamicQuery etc..)
                                if (code == None) :
                                    continue
                                SetQueryList = getSetQuery.findall(code)
                                for i in range(len(SetQueryList)) :
                                    SetQueryParser(SetQueryList[i], QueryDict3, Metapath, None, QueryLists)
                        # 한 method 안에 여러 docall들이 불리고, 이 docall 안에 여러 쿼리문들이 있을수 있음 (확인필요)
                        for doCall in BOmethod.iter('{http://www.tmax.co.kr/proobject/flow}dataObjectCall') :

                            afterCode = doCall.find('{http://www.tmax.co.kr/proobject/flow}afterCode')
                            beforeCode = doCall.find('{http://www.tmax.co.kr/proobject/flow}beforeCode')

                            if (beforeCode != None) :
                                code = beforeCode.text
                                if (code != None) :
                                    SetQueryList = getSetQuery.findall(code)
                                    for i in range(len(SetQueryList)) :
                                        SetQueryParser(SetQueryList[i], QueryDict3, Metapath, doCall, QueryLists)
                            if (afterCode != None) :
                                code = afterCode.text
                                if (code != None) :
                                    SetQueryList = getSetQuery.findall(code)
                                    for i in range(len(SetQueryList)) :
                                        SetQueryParser(SetQueryList[i], QueryDict3, Metapath, doCall, QueryLists)
                            # method 가 접근하는 DOF 이름 얻어오기.
                            DOFname = doCall.find('{http://www.tmax.co.kr/proobject/flow}instanceInfo/{http://www.tmax.co.kr/proobject/flow}classInfo').get('className')
                            DofPathInfo = doCall.find('{http://www.tmax.co.kr/proobject/flow}instanceInfo/{http://www.tmax.co.kr/proobject/flow}classInfo').get('classPackageName') + "." + DOFname
                            DofPathInfoList = DofPathInfo.split(".")
                            DofPathInfoList[len(DofPathInfoList)-1] = DofPathInfoList[len(DofPathInfoList)-1] + ".factory"
                            DofInfoPath = DofPathInfoList[0]
                            for i in range(len(DofPathInfoList) -1) :
                                DofInfoPath = os.path.join(DofInfoPath, DofPathInfoList[i+1])
                            DOFpath = os.path.join(Metapath, DofInfoPath)
                            #DOFpath = Metapath + "/" + doCall.find('{http://www.tmax.co.kr/proobject/flow}instanceInfo/{http://www.tmax.co.kr/proobject/flow}classInfo').get('classPackageName').replace('.','/') + '/' + DOFname + '.factory'
                            if (os.path.isfile(DOFpath) == False) :
                                QueryDict3["ERROR"] = "PARSING_SERVER_ERROR : 잘못된 DOF 경로 입니다. 쓰이지 않는 DOF 이거나, 빌드가 안된 DOF 이므로 영향도 분석에서 제외하겠습니다."
                                QueryLists.append(QueryDict3)
                                continue
                                #print("잘못된 DOF 경로 입니다. 쓰이지 않는 DOF 이거나, 빌드가 안된 DOF 이므로 영향도 분석에서 제외하겠습니다.")
                            # DOF에서 쿼리문 alias 가져오기.
                            # fullstatement 가 있다면 BO에 DOF를 연결하여 만든 alias를 썼다는 뜻
                            if (doCall.find('{http://www.tmax.co.kr/proobject/flow}fullStatement') != None) :
                                QueryDict4 = copy.deepcopy(QueryDict3)
                                #print(DOFname)
                                QueryDict4["DOF_NAME"] = DOFname
                                QueryName = doCall.find('{http://www.tmax.co.kr/proobject/flow}fullStatement').get('alias')
                                QueryDict4["QUERY_NAME"] = QueryName

                                # DOF 이름으로 DOF 파일 접근하여 쿼리문 가져오기.
                                DOFtree = elemTree.parse(DOFpath)
                                DOFroot = DOFtree.getroot()
                                QueryExtractor(QueryDict4, DOFtree, QueryName, DofFullstatements, QueryLists)

                            if (doCall.find('{http://www.tmax.co.kr/proobject/flow}dynamicStatement') != None) :
                                QueryDict4 = copy.deepcopy(QueryDict3)
                                QueryDict4["DOF_NAME"] = DOFname
                                QueryName = doCall.find('{http://www.tmax.co.kr/proobject/flow}dynamicStatement').get('alias')
                                QueryDict4["QUERY_NAME"] = QueryName

                                DOFtree = elemTree.parse(DOFpath)
                                DOFroot = DOFtree.getroot()
                                QueryExtractor(QueryDict4, DOFtree, QueryName, DofDynamicstatements, QueryLists)
    return QueryLists

if __name__ == '__main__' :

    UserPath = input('servicegroup.xml 경로를 입력해 주세요 : ')
    a = PoParser(UserPath)
    print(a[0])
    print(len(a))
