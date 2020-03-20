import xml.etree.ElementTree as elemTree
import re
import copy
import os

#Query를 저장하기 위한 list,
# 각각의 원소는 [APP,SG, meta, com, tmax, ...depths, so, SoName, BoName, MethodName, DofName, QueryAliasName, Query] 로 구성된다.
QueryLists = []
Querys = []
# string 파싱용
# 개발자가 BO에 query문을 실행할 때, 버츄얼모듈이나, aftercode에 직접 손코딩을 할 수도 있다.
# 이부분은 손코딩한 부분을 string으로 전부 가져와 setQuery 함수를 실행한 부분을 파싱해온다.
getSetQuery = re.compile("setFullQuery[(]\S+|setDynamicQuery[(]\S+|setUserQuery[(]\S+")
getAlias = re.compile("QUERY[.]\w+")


##TODO path 는 나중에 input으로 바뀌어야 할듯, 함수화 해서 SGpath 나, SGpath의 list를 input으로 받도록 수정해야함. ##
SGpath = 'C:/FS/CORE/META-INF/servicegroup.xml'
SGtree = elemTree.parse(SGpath)
SGroot = SGtree.getroot()

# app이름, sg이름은 SG파일에 존재.
# 위 2개를 이용하여 meta의 경로도 지정해 준다.
AppName = SGroot.get("ApplicationName")
SgName = SGroot.get("serviceGroupName")
Metapath = "C:/" + AppName + "/" + SgName + "/meta/"

# SG 내부의 SO 이름 및 경로들을 가져오기 위한 로직 시작.
ns21 = SGroot.tag
SOroot = ns21.replace('service-group','service-object')
classname = ns21.replace('service-group','class-name')
name = ns21.replace('service-group','name')

# 아래 주석들은 필요없는 path 및 root들. 추후 삭제 필요.
# path = 'C:/Users/Tmax/git/FS/FS/WS/meta/com/tmax/infra/client/'
# tree = elemTree.parse('C:/Users/Tmax/git/FS/FS/WS/meta/com/tmax/infra/client/so/DeleteClientTable1SO.so')
# root = tree.getroot()


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

for SO in SGroot.iter(SOroot) :
    # QueryLists에 담기위한 하나의 QueryList 생성
    QueryList = []
    QueryList.append(AppName)
    QueryList.append(SgName)
    QueryList.append("meta")

    # SO 파일에 도달하기 위한 디렉토리 파싱 (ex. com/tmax/infra...)
    SOclassname = SO.find(classname)
    directory = SOclassname.text.split(".")

    # directory-1을 하는 이유는 가장 마지막은 SO이름으로 되어있기 때문
    for i in range(len(directory)-1) :
        #print(directory[i])
        QueryList.append(directory[i])
        
    SOname = SO.find(name).text
    QueryList.append(SOname)
    # SO파일 파싱
    SOpath = Metapath + SOclassname.text.replace('.', '/') + '.so'

    if (os.path.isfile(SOpath) == False) :
        QueryList.append("SO path error")
        #print(QueryList)
        continue

    tree = elemTree.parse(SOpath)
    root = tree.getroot()
    #print(QueryList)

# SO 에서 bizMethodCall 에 의해 bo가 불린다.
##TODO 버츄얼 모듈을 통해 bo를 콜 할수도 있다. 이부분 추가 코딩 필요. ## 
    for boCall in root.iter(bizMethodCall) :

        # bo가 여러개일 경우 위에서만든 QueryList 가 중복해서 여러개 필요하므로 깊은복사.
        QueryList2 = copy.deepcopy(QueryList)
        
        # bo 이름,경로가져오기.
        BoVariableName = boCall.find(bizInstanceInfo).get('variableName')
        for variable in root.iter(SoVariable) :
            if (variable.get('name') == BoVariableName) :
                BoInf = variable.find(userDefined).text
                break
        BoInfs = BoInf.split(".")
        BoName = BoInfs[len(BoInfs)-1]
        QueryList2.append(BoName)
        BOpath = Metapath + BoInf.replace('.', '/') + '.bo'
        #print(QueryList2)
       
        # bo 안의 메서드들 가져오기 (이 메서들마다 여러 쿼리가 존재할 수 있음, 쿼리는 dof로 부터 가져온다.).
        for method in boCall.findall(BoMethods) :
            QueryList3 = copy.deepcopy(QueryList2)
            MethodName = method.get('methodName')
            QueryList3.append(MethodName)
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
                            
                            # 쿼리문을 전부 가져와 쿼리가 호출될 dof 이름과, 호출된 쿼리 alias 이름을 parsing 해오는 for문
                            ##TODO 뒤에서 aftercode를 serach 할때도 같은 로직이 들어감 -> 함수화 필요 ##
                            for i in range(len(SetQueryList)) :
                                SetQueryList[i] = SetQueryList[i].replace("setFullQuery(","").replace("setDynamicQuery(","").replace("setUserQuery(","")
                                SetQueryList[i] = SetQueryList[i].replace(");","")
                                QueryInf = SetQueryList[i].split("QUERY.")
                                QueryInf[0] = QueryInf[0].replace(".FULL","")
                                QueryInf[0] = QueryInf[0].replace(".DYNAMIC","")
                                QueryInf[0] = QueryInf[0].replace(".USER","")
                                DofPathInfs = QueryInf[0].split(".")
                                if (len(DofPathInfs) >= 2) :
                                    DofPath = Metapath + QueryInf[0].replace(".","/") + ".factory"
                                else :
                                    DofName = DofPathInfs[len(DofPathInfs)-1]
                                    for classinfo in doCall.iter('{http://www.tmax.co.kr/proobject/flow}classInfo') :
                                        if (classinfo.get("className") == DofName) :
                                            DofPathInf = classinfo.get("classPackageName")
                                            break
                                    DofPath = Metapath + DofPathInf.replace(".","/") +"/" + DofName + ".factory"
                                AliasName = QueryInf[1]

                                # DOF 경로를 토대로 DOF 파일 파싱
                                DOFtree = elemTree.parse(DofPath)
                                DOFroot = DOFtree.getroot()

                                # DOF이름, DOF에서 호출될 쿼리 alias이름을 list에 담는다.
                                QueryList4 = copy.deepcopy(QueryList3)
                                QueryList4.append(DOFroot.get("logicalName"))
                                QueryList4.append(AliasName)
                            
                                for fullstatements in DOFtree.iter(DofFullstatements) :
                                    if (fullstatements.get('alias') == AliasName) :
                                        Query = fullstatements.find(DofStatement).text
                                        QueryList4.append(Query)
                                        Querys.append(Query)
                                        #print(QueryList4)
                                        # 쿼리문까지 도달했으므로 하나의 리스트 완성. 원래의 QueryLists에 append 해준다.
                                        QueryLists.append(QueryList4)
                                        
                                for dynamicstatements in DOFtree.iter(DofDynamicstatements) :
                                    if (dynamicstatements.get('alias') == AliasName) :
                                        Query = dynamicstatements.find(DofStatement).text
                                        QueryList4.append(Query)
                                        Querys.append(Query)
                                        #print(QueryList4)
                                        QueryLists.append(QueryList4)
                                        
                                
                    ##TODO 여기부터 리팩토링 필요
                    # 한 method에 여러 쿼리문이 있을 수 있음
                    # 한 method 안에 여러 docall들이 불리고, 이 docall 안에 여러 쿼리문들이 있을수 있음 (확인필요)
                    for doCall in BOmethod.iter('{http://www.tmax.co.kr/proobject/flow}dataObjectCall') :

                        afterCode = doCall.find('{http://www.tmax.co.kr/proobject/flow}afterCode')
                        beforeCode = doCall.find('{http://www.tmax.co.kr/proobject/flow}beforeCode')

                        if (beforeCode != None) :
                            code = beforeCode.text
                            if (code != None) :
                                SetQueryList = getSetQuery.findall(code)
                                for i in range(len(SetQueryList)) :
                                    SetQueryList[i] = SetQueryList[i].replace("setFullQuery(","").replace("setDynamicQuery(","").replace("setUserQuery(","")
                                    SetQueryList[i] = SetQueryList[i].replace(");","")
                                    QueryInf = SetQueryList[i].split("QUERY.")
                                    QueryInf[0] = QueryInf[0].replace(".FULL","")
                                    QueryInf[0] = QueryInf[0].replace(".DYNAMIC","")
                                    QueryInf[0] = QueryInf[0].replace(".USER","")
                                    DofPathInfs = QueryInf[0].split(".")
                                    if (len(DofPathInfs) >= 2) :
                                        DofPath = Metapath + QueryInf[0].replace(".","/") + ".factory"
                                    else :
                                        DofName = DofPathInfs[len(DofPathInfs)-1]
                                        for classinfo in doCall.iter('{http://www.tmax.co.kr/proobject/flow}classInfo') :
                                            if (classinfo.get("className") == DofName) :
                                                DofPathInf = classinfo.get("classPackageName")
                                                break
                                        DofPath = Metapath + DofPathInf.replace(".","/") +"/" + DofName + ".factory"
                                    AliasName = QueryInf[1]
                                    QueryList4 = copy.deepcopy(QueryList3)
                                    if (os.path.isfile(DofPath) == False) :
                                        QueryList4.append("DOF path error")
                                        #print(QueryList4)
                                        continue
                                    
                                    DOFtree = elemTree.parse(DofPath)
                                    DOFroot = DOFtree.getroot()
                                    #print(QueryList3)
                                    #print(QueryList4)
                                    #print(DOFroot.get("logicalName"))
                                    QueryList4.append(DOFroot.get("logicalName"))
                                    #print(AliasName)
                                    QueryList4.append(AliasName)
                                    
                                    for fullstatements in DOFtree.iter('{http://www.tmax.co.kr/proobject/dataobjectfactory}fullstatements') :
                                        if (fullstatements.get('alias') == AliasName) :
                                            #print(fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text)
                                            Query = fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text
                                            QueryList4.append(Query)
                                            #print(QueryList4)
                                            QueryLists.append(QueryList4)
                                            Querys.append(Query)

                                    for dynamicstatements in DOFtree.iter(DofDynamicstatements) :
                                        if (dynamicstatements.get('alias') == AliasName) :
                                            Query = dynamicstatements.find(DofStatement).text
                                            QueryList4.append(Query)
                                            #print(QueryList4)
                                            QueryLists.append(QueryList4)
                                            Querys.append(Query)
                        
                        if (afterCode != None) :
                            code = afterCode.text
                            if (code != None) :
                                SetQueryList = getSetQuery.findall(code)
                                for i in range(len(SetQueryList)) :
                                    SetQueryList[i] = SetQueryList[i].replace("setFullQuery(","").replace("setDynamicQuery(","").replace("setUserQuery(","")
                                    SetQueryList[i] = SetQueryList[i].replace(");","")
                                    QueryInf = SetQueryList[i].split("QUERY.")
                                    QueryInf[0] = QueryInf[0].replace(".FULL","")
                                    QueryInf[0] = QueryInf[0].replace(".DYNAMIC","")
                                    QueryInf[0] = QueryInf[0].replace(".USER","")
                                    DofPathInfs = QueryInf[0].split(".")
                                    
                                    if (len(DofPathInfs) >= 2) :
                                        DofPath = Metapath + QueryInf[0].replace(".","/") + ".factory"
                                    else :
                                        DofName = DofPathInfs[len(DofPathInfs)-1]
                                        for classinfo in doCall.iter('{http://www.tmax.co.kr/proobject/flow}classInfo') :
                                            if (classinfo.get("className") == DofName) :
                                                DofPathInf = classinfo.get("classPackageName")
                                                break
                                        DofPath = Metapath + DofPathInf.replace(".","/") +"/" + DofName + ".factory"

                                    AliasName = QueryInf[1]
                                    DOFtree = elemTree.parse(DofPath)
                                    DOFroot = DOFtree.getroot()
                                    QueryList4 = copy.deepcopy(QueryList3)
                                    #print(QueryList3)
                                    #print(QueryList4)
                                    #print(DOFroot.get("logicalName"))
                                    QueryList4.append(DOFroot.get("logicalName"))
                                    #print(AliasName)
                                    QueryList4.append(AliasName)
                                    #print(QueryList4)
                                    
                                    for fullstatements in DOFtree.iter('{http://www.tmax.co.kr/proobject/dataobjectfactory}fullstatements') :
                                        if (fullstatements.get('alias') == AliasName) :
                                            #print(fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text)
                                            Query = fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text
                                            QueryList4.append(Query)
                                            #print(QueryList4)
                                            QueryLists.append(QueryList4)
                                            Querys.append(Query)
                                            
                                    for dynamicstatements in DOFtree.iter(DofDynamicstatements) :
                                        if (dynamicstatements.get('alias') == AliasName) :
                                            Query = dynamicstatements.find(DofStatement).text
                                            QueryList4.append(Query)
                                            #print(QueryList4)
                                            QueryLists.append(QueryList4)
                                            Querys.append(Query)
                            
                        # method 가 접근하는 DOF 이름 얻어오기.
                        DOFname = doCall.find('{http://www.tmax.co.kr/proobject/flow}instanceInfo/{http://www.tmax.co.kr/proobject/flow}classInfo').get('className')
                        DOFpath = Metapath + doCall.find('{http://www.tmax.co.kr/proobject/flow}instanceInfo/{http://www.tmax.co.kr/proobject/flow}classInfo').get('classPackageName').replace('.','/') + '/' + DOFname + '.factory'

                        # DOF에서 쿼리문 alias 가져오기.
                        # 수정필요. docall 하나에 여러 쿼리문이 들어갈 수 있다.
                        # fullstatement 가 있다면 BO에 DOF를 연결하여 만든 alias를 썼다는 뜻
                        if (doCall.find('{http://www.tmax.co.kr/proobject/flow}fullStatement') != None) :
                            QueryList4 = copy.deepcopy(QueryList3)
                            #print(DOFname)
                            QueryList4.append(DOFname)
                            QueryName = doCall.find('{http://www.tmax.co.kr/proobject/flow}fullStatement').get('alias')
                            QueryList4.append(QueryName)

                            # DOF 이름으로 DOF 파일 접근하여 쿼리문 가져오기.
                            DOFtree = elemTree.parse(DOFpath)
                            DOFroot = DOFtree.getroot()

                        # 쿼리문 찾기
                            for fullstatements in DOFtree.iter('{http://www.tmax.co.kr/proobject/dataobjectfactory}fullstatements') :
                                if (fullstatements.get('alias') == QueryName) :
                                    #print(fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text)
                                    Query = fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text
                                    QueryList4.append(Query)
                                    #print(QueryList4)
                                    QueryLists.append(QueryList4)
                                    Querys.append(Query)
                                    
                        if (doCall.find('{http://www.tmax.co.kr/proobject/flow}dynamicStatement') != None) :
                            QueryList4 = copy.deepcopy(QueryList3)
                            QueryList4.append(DOFname)
                            QueryName = doCall.find('{http://www.tmax.co.kr/proobject/flow}dynamicStatement').get('alias')
                            QueryList4.append(QueryName)

                            DOFtree = elemTree.parse(DOFpath)
                            DOFroot = DOFtree.getroot()
                            
                            for dynamicstatements in DOFtree.iter('{http://www.tmax.co.kr/proobject/dataobjectfactory}dynamicstatements') :
                                if (dynamicstatements.get('alias') == QueryName) :
                                    #print(fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text)
                                    Query = dynamicstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text
                                    QueryList4.append(Query)
                                    #print(QueryList4)
                                    QueryLists.append(QueryList4)
                                    Querys.append(Query)
print(QueryLists)
print(Querys)
#for data in root.findall(x):
#   for child in data :
#        print(child.get('id'))
    
#for event in root.iter('{http://www.tmaxsoft.com/top/SNAPSHOT/resource}Event'):
#   for child in root.iter()
#        for child2 in child
#            if child2.
#    print(a.getattribute)
#    print(event.attrib) event 찾고 다시 처음부터 포문돌려서 그 event 엄마 찾도록 해야할듯
