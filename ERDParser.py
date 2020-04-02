import sys

def ERDparser(inputFile) :
#inputFile = "Copy of Copy of PS_TIMS_cys.sql" # sql 파일
## ToDo: 커넥터로부터 얻어온 임의의 sql 문서에 대해서 처리하도록 변경 필요
    sqlFile = open(inputFile, 'r') # sql이 담긴 파일을 읽음

    sys.stdout = open("Output_list.txt", 'w') # 아웃풋 리스트를 출력 형태로 출력

    List = [] # 출력 리스트 초기화

    while True: # line by line으로 읽어내리는 while문

        line = sqlFile.readline() # 파일을 한 줄 씩 읽음

        if 'CREATE TABLE'in line: # CREATE TABLE이 포함된 라인인지 체크

            # 변수 초기화
            table_name = '' # 테이블 이름을 담을 변수
            columnList_name = [] # 컬럼명을 담을 리스트 변수
            columnList_type = [] # 컬럼타입을 담을 리스트 변수

            ERDdict = {} # 딕셔너리 변수

            table_name = line.split()[2].replace('`', '', 2) # 테이블 이름 정보를 변수에 담음
    
            while True: # 아래 나열되는 컬럼명을 line by line으로 읽어내림
      
                line = sqlFile.readline() # 파일을 한 줄 씩 읽음

                if line[0:2] == "	`": # 컬럼 명이 입력되는 형식이 맞는지 확인
        
                    columnList_name.append(line.split()[0].replace('`', '', 2))
                    columnList_type.append(line.split()[1].replace('`', '', 2))
                    # 컬럼명과 컬럼 타입을 아웃풋 리스트에 어펜드

                if (line == ');\n') or not line: # CREATE TABLE 쿼리가 끝나면 
                    ERDdict["TABLE"] = table_name # ERDdict에 테이블 이름과 컬럼명을 담음
                    ERDdict["COLUMN"] = columnList_name
        
                    List.append(ERDdict) # 딕셔너리를 출력 리스트에 어펜드
                    break # CREATE TABLE이 끝나거나 파일 끝까지 읽었으니 while문 종료
  
        if not line: break # 파일 끝까지 읽었으면 while문 종료

#print(Li # 아웃풋 txt 파일에 리스트를 출력

    sqlFile.close() # 파일 닫기
    return List
