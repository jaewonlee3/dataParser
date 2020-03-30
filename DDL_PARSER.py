sqlFile = open("Copy of Copy of PS_TIMS_cys.sql", 'r') # sql이 담긴 파일을 읽음
## ToDo: 커넥터로부터 얻어온 임의의 sql 문서에 대해서 처리하도록 변경 필요

outputFile = open("Output_list.txt", 'w') # 아웃풋 리스트 출력
## ToDo: 아웃풋 형식에 맞는 문서를 변경


while True: # line by line으로 읽어내리는 while문

  line = sqlFile.readline() # 파일을 한 줄 씩 읽음

  if 'CREATE TABLE'in line: # 읽은 줄의 첫 11자가 CREATE TABLE인지 판단

    print('TBL : ' + line.split()[2].replace('`', '', 2)) # 테이블 이름 콘솔에 출력

    outputFile.write('[' + line.split()[2].replace('`', '', 2) + ']\n') # 테이블 이름을 아웃풋 리스트에 출력
    ## ToDo: 아웃풋 리스트 양식 정의에 맞춰서 변경 필요

    while True: # 아래 나열되는 컬럼명을 line by line으로 읽어내림
      
      line = sqlFile.readline() # 파일을 한 줄 씩 읽음
      
      if (line == ');\n') or not line: break # CREATE TABLE이 끝나거나 파일 끝까지 읽었으면 while문 종료

      if line[0:2] == "	`": # 컬럼 명이 입력되는 형식이 맞는지 확인
      
        print('  col : ' + line.split()[0].replace('`', '', 2)+ ' [' + line.split()[1]+']') # 컬럼명과 컬럼 타입을 콘솔에 출력
      
        outputFile.write('  {' + line.split()[0].replace('`', '', 2))
        outputFile.write(' ' + line.split()[1].replace('`', '', 2) + '}\n') 
        # 컬럼명과 컬럼 타입을 아웃풋 리스트에 출력
        ## ToDo: 아웃풋 리스트 양식 정의에 맞춰서 변경 필요

  if not line: break # 파일 끝까지 읽었으면 while문 종료


sqlFile.close() # 파일 닫기
outputFile.close()