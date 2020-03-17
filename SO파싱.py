import xml.etree.ElementTree as elemTree
import re
import copy

#Query를 저장하기 위한 list,
# 각각의 원소는 [APP,SG, meta, com, tmax, ...depths, so, SoName, BoName, MethodName, DofName, QueryAliasName, Query] 로 구성된다.
QueryLists = []

# string 파싱용
# 개발자가 BO에 query문을 실행할 때, 버츄얼모듈이나, aftercode에 직접 손코딩을 할 수도 있다.
# 이부분은 손코딩한 부분을 string으로 전부 가져와 setQuery 함수를 실행한 부분을 파싱해온다.
getSetQuery = re.compile("Query[(]\S+")
getAlias = re.compile("QUERY[.]\w+")


## path 는 나중에 input으로 바뀌어야 할듯, 함수화 해서 SGpath 나, SGpath의 list를 input으로 받도록 수정해야함. ##
SGpath = 'C:/Users/Tmax/git/FS/FS/WS/META-INF/servicegroup.xml'
SGtree = elemTree.parse(SGpath)
SGroot = SGtree.getroot()

# app이름, sg이름은 SG파일에 존재.
# 위 2개를 이용하여 meta의 경로도 지정해 준다.
AppName = SGroot.get("ApplicationName")
SgName = SGroot.get("serviceGroupName")
Metapath = "C:/Users/Tmax/git/FS/" + AppName + "/" + SgName + "/meta/"

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
bizMethodCall = '{http://www.tmax.co.kr/proobject/flow}bizMethodCall'
bizClassInfo = '{http://www.tmax.co.kr/proobject/flow}bizInstanceInfo/{http://www.tmax.co.kr/proobject/flow}classInfo'
bizMethod = '{http://www.tmax.co.kr/proobject/bizobject}bizMethod'
BoMethods = '{http://www.tmax.co.kr/proobject/flow}method'

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
    tree = elemTree.parse(SOpath)
    root = tree.getroot()

# SO 에서 bizMethodCall 에 의해 bo가 불린다.
## 버츄얼 모듈을 통해 bo를 콜 할수도 있다. 이부분 추가 코딩 필요. ## 
    for boCall in root.iter(bizMethodCall) :

        # bo가 여러개일 경우 위에서만든 QueryList 가 중복해서 여러개 필요하므로 깊은복사.
        QueryList2 = copy.deepcopy(QueryList)
        
        # bo 이름,경로가져오기.
        BOname = boCall.find(bizClassInfo).get('className')
        QueryList2.append(BOname)
        BOpath = Metapath + boCall.find(bizClassInfo).get('classPackageName').replace('.', '/') + '/' + BOname + '.bo'
       
        # bo 안의 메서드들 가져오기 (이 메서들마다 여러 쿼리가 존재할 수 있음, 쿼리는 dof로 부터 가져온다.).
        for method in boCall.findall(BoMethods) :
            QueryList3 = copy.deepcopy(QueryList2)
            MethodName = method.get('methodName')
            #print(MethodName)
            QueryList3.append(MethodName)

            # bo 이름으로 bo 파일을 오픈하여, method 안에 담긴 퀴리문 가져오기.
            BOtree = elemTree.parse(BOpath)
            BOroot = BOtree.getroot()
            
            # 위에서 얻은 method 이름으로 bo 파일 내부의 method 정보를 찾는다.
            for BOmethod in BOroot.iter(bizMethod) :
                if (BOmethod.get('methodName') == MethodName) :
                    
                    for virtualModule in BOmethod.iter('{http://www.tmax.co.kr/proobject/flow}virtualModule') :
                        if (virtualModule != None) :
                            code = virtualModule.find('{http://www.tmax.co.kr/proobject/flow}code').text
                            SetQueryList = getSetQuery.findall(code)
                            
                            for i in range(len(SetQueryList)) :
                                SetQueryList[i] = SetQueryList[i].replace("Query(","")
                                SetQueryList[i] = SetQueryList[i].replace(");","")
                                QueryInf = SetQueryList[i].split("DOF")
                                DofPath = QueryInf[0].replace(".","/") + "DOF.factory"
                                AliasNames = getAlias.findall(Queryinf[1])
                                AliasName = AliasNames.replace("QUERY.","")
                                DOFtree = elemTree.parse(DofPath)
                                DOFroot = DOFtree.getroot()
                                QueryList4 = copy.deepcopy(QueryList3)
                                #print(DOFroot.get("logicalName"))
                                QueryList4.append(DOFroot.get("logicalName"))
                                QueryList4.append(AliasName)
                                
                                
                                for fullstatements in DOFtree.iter('{http://www.tmax.co.kr/proobject/dataobjectfactory}fullstatements') :
                                    if (fullstatements.get('alias') == AliasName) :
                                        Query = fullstatements.find('{http://www.tmax.co.kr/proobject/dataobjectfactory}statement').text
                                        QueryList4.append(Query)
                                        QueryLists.append(QueryList4)
                                        
                                

                    # 한 method에 여러 쿼리문이 있을 수 있음
                    # 한 method 안에 여러 docall들이 불리고, 이 docall 안에 여러 쿼리문들이 있을수 있음 (확인필요)
                    for doCall in BOmethod.iter('{http://www.tmax.co.kr/proobject/flow}dataObjectCall') :

                        afterCode = doCall.find('{http://www.tmax.co.kr/proobject/flow}afterCode')
                        if (afterCode != None) :
                            code = afterCode.text
                            if (code != None) :
                                SetQueryList = getSetQuery.findall(code)
                                
                                for i in range(len(SetQueryList)) :
                                    SetQueryList[i] = SetQueryList[i].replace("Query(","")
                                    SetQueryList[i] = SetQueryList[i].replace(");","")
                                    QueryInf = SetQueryList[i].split("DOF")
                                    DofPath = Metapath + QueryInf[0].replace(".","/") + "DOF.factory"
                                    AliasNames = getAlias.findall(QueryInf[1])
                                    AliasName = AliasNames[0].replace("QUERY.","")
                                    DOFtree = elemTree.parse(DofPath)
                                    DOFroot = DOFtree.getroot()
                                    QueryList4 = copy.deepcopy(QueryList3)
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
                                            QueryLists.append(QueryList4)
                            
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
                            #print(QueryName)
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
                                QueryLists.append(QueryList4)
           
for i in range(len(QueryLists)) :
    print(QueryLists[i])

#for data in root.findall(x):
#   for child in data :
#        print(child.get('id'))
    
#for event in root.iter('{http://www.tmaxsoft.com/top/SNAPSHOT/resource}Event'):
#   for child in root.iter()
#        for child2 in child
#            if child2.
#    print(a.getattribute)
#    print(event.attrib) event 찾고 다시 처음부터 포문돌려서 그 event 엄마 찾도록 해야할듯
