## -*- coding: UTF-8 -*-

import sqlparse
from array import *

class RecursiveTokenParser(object):
    def __init__(self, query):
        self.query = query
        self.names = []
        self.elements = sqlparse.parse(self.query)
        self.stmt = self.elements[0]
        self.info = []
        self.parsedToken = []
        self.DML = ["SELECT", "INSERT", "UPDATE", "DELETE"]

    def extractColumn(self):
        #query type을 가져오는 함수 -> tokenReport에서 query type에 따라 처리방식 결정
        query_type = self.stmt.get_type()
        #print("This is a "+ query_type+" query")
        #입력한 query를 token화 시켜주는 함수
        for token in self.stmt.tokens:
            self.parseToken(token)
        return self.tokenReport(query_type, self.parsedToken)


    #Query Analyser
    #Input:
    #   query_type: query type에 따라 처리 방식이 존재
    #       INSERT, UPDATE, DELETE, SELECT query 형식
    #   parsedToken: query의 token을 담고있는 List
    #Output:
    #   return: self.info -> [[schemaName,tableName,columnName],[],[]]
    def tokenReport(self, query_type, parsedToken):
        #insert query 분석
        #insert query 형식:
        #   INSERT INTO SCHEMA.TABLE (column 정보) VALUE (값 정보)
        if query_type == "INSERT":
            # insert query의 시작은 항상 (INSERT) INTO SCHEMA.TABLE이기 때문에
            # 1,3 번 index로 스키마랑 테이블 이름 추출
            schemaName = parsedToken[1]
            tableName = parsedToken[3]
            # 스키마,테이블은 사용했으니 iter에서는 그 다음 index부터 돌린다.
            for token in parsedToken[4:]:
                #column 이름 정보 빼고는 관심이 없기때문에 예외처리로 걸러낸다
                if token == "(" or token == ",":
                    continue
                #insert query에서 VALUE (값 정보)는 필요없어서 첫 ()이 끝나는
                #시점으로 break를 해준다
                elif token == ")":
                    break
                #위에 명시된 예외처리 된 내용이 아니라면 column 정보
                #self.info에 담는다
                else:
                    self.info.append([schemaName, tableName, token])
            return self.info



        #update query 분석
        #update query 형식:
        #   UPDATE SCHEMA.TABLE SET column정보1,column정보2,....column정보N WHERE -> column정보
        #                                                             ㄴ> subquery 정보
        elif query_type == "UPDATE":
            #update query는 UPDATE 다음 무조건 스키마 이름. 테이블 이름 형태
            # 0,2 index로 추출
            schemaName = parsedToken[0]
            tableName = parsedToken[2]
            #넘겨준
            for index, token in enumerate(parsedToken):
                whereCount = 0
                subqueryCount = 0
                #column 정보는 column이름 = 값 형태임으로 "=" 앞의 정보로 column이름 추출
                if token == "=":
                    columnInfo = [schemaName,tableName,parsedToken[index-1]]
                    if columnInfo not in self.info:
                        self.info.append(columnInfo)
                #WHERE 후에는 두가지 가능성 존재
                #   1. column 정보: column이름 = 값
                #      "="를 찾아서 위랑 똑같이 처리한다
                #   2. Subquery 정보: (SELECT QUERY)
                #       괄호 사이의 정보를 추출해서 tokenReport로 SELECT 형태로 다시 돌린다
                elif token == "WHERE" and whereCount == 0:
                    whereCount += 1
                    tokenWhereEnd = parsedToken[index:]
                    # #print(tokenWhereEnd)
                    for subindex, token in enumerate(tokenWhereEnd):
                        if token == "(":
                            subqueryCount += 1
                            if subqueryCount == 1:
                                tokenSubQuery = tokenWhereEnd[subindex+1:]
                                self.tokenReport("SELECT", tokenSubQuery)
                            elif token == ")":
                                subqueryCount -=1

            return self.info



        #delete query 분석
        #delete query 형식:
        #   DELETE FROM SCHEMA.TABLE WHERE -> column 정보
        #                               ㄴ> subquery 정보
        elif query_type == "DELETE":
            whereCount = 0
            subqueryCount = 0
            #delete query 시작은 무조건 DELETE FROM SCHEMA.TABLE
            #1,3 index로 delete target table 정보 추출
            schemaName = parsedToken[1]
            tableName = parsedToken[3]
            for index, token in enumerate(parsedToken):
                #token이 첫번째 WHERE일시 IF 문 통과
                #token을 돌면서 subquery안에 있는 WHERE를 반복으로 도는것을 방지
                if token == "WHERE" and whereCount == 0:
                    whereCount += 1
                    #WHERE token부터 query의 끝까지 다시 iter
                    tokenWhereEnd = parsedToken[index:]
                    for subindex, token in enumerate(tokenWhereEnd):
                        #WHERE 후에 (는 subquery를 의미
                        #subquery경우 () 안의 내용을 list로 만들어서 다시
                        #tokenReport에 SELECT Query형식으로 던진다
                        if token == "(":
                            subqueryCount += 1
                            if subqueryCount == 1:
                                tokenSubQuery = tokenWhereEnd[subindex+1:]
                                self.tokenReport("SELECT", tokenSubQuery)
                        #columnName=값 -> = 앞의 index로 column 이름 추출
                        #subquery==0에서만 작동
                        #subquery안의 column이름은 위의 subquery 처리 부분에서 추출
                        elif token == "=" and subqueryCount == 0:
                            columnInfo = [schemaName,tableName,tokenWhereEnd[subindex-1]]
                            #반복된 column 정보를 막기위해, self.info에 존재하는
                            #check하고 존재하지 않을 경우에만 self.info에 append
                            if columnInfo not in self.info:
                                self.info.append(columnInfo)
                        #")"는 subquery의 끝을 의미함 -> subqueryCount를 낮춰준다
                        elif token == ")":
                            subqueryCount -= 1

            return self.info



        #select query 분석
        #select query 형식:
        #   SELECT TABLE.COLUMN FROM SCHEMA.TABLE WHERE -> column 정보
        #                                           ㄴ> subquery 정보
        #TODO: subquery ALIAS 경우 처리 추가
        elif query_type == "SELECT" :
            tableInfo = []
            columnName = []
            for index, token in enumerate(parsedToken):
                #SELECT QUERY는 FROM 앞에는 select할 컬럼 내용이 존재,
                #뒤에는 SCHEMA.TABLE 정보가 존재
                if token == "FROM":
                    #query시작부터 FROM 토큰까지 iter를 톨면서 . token의 인덱스에서
                    #앞뒤 인덱스로 table(alias).column 정보 추출
                    tokenStartFrom = parsedToken[:index]
                    for subindex, token in enumerate(tokenStartFrom):
                        if token == ".":
                            columnName.append([parsedToken[subindex-1], parsedToken[subindex+1]])
                    #SELECT는 table정보를 AS를 통해 ALIAS해서 사용
                    #FROM token부터 WHERE token까지 iter를 돌면서 "AS" 토큰
                    #인덱스에서 앞뒤의 인덱스들로 schema, table 정보 추출
                    tokenFromEnd = parsedToken[index:]
                    for subindex, token in enumerate(tokenFromEnd):
                        if token == "AS":
                            tableInfo.append([tokenFromEnd[subindex-3],tokenFromEnd[subindex-1],tokenFromEnd[subindex+1]])
                        #WHERE 토큰은 아래서 처리 하기때문에
                        #첫 WHERE가 나오면 break
                        elif token == "WHERE":
                            break
                #WHERE token일 경우 WHERE부터 query 끝까지 돌면서 columnName 추출
                #( token의 경우 subquery의 시작이기때문에 (부터의 내용을 담아서
                #다시 tokenReport에 던진다
                elif token == "WHERE":
                    whereCount = 1
                    tokenWhereEnd = parsedToken[index:]
                    for subindex, token  in enumerate(tokenWhereEnd):
                        if token == ".":
                            columnName.append([tokenWhereEnd[subindex-1], tokenWhereEnd[subindex+1]])
                        elif token == "(":
                            tokenSubQuery = tokenWhereEnd[subindex+1:]
                            self.tokenReport("SELECT", tokenSubQuery)
                            break

                    whereCount = 0
            # output형식 맞춰주는 로직
            for column in columnName:
                if len(column) > 1:
                    tableAlias = column[0]
                    for ti in tableInfo:
                        if tableAlias == ti[-1]:
                            columnInfo = [ti[0],ti[1],column[1]]
                            if columnInfo not in self.info:
                                self.info.append([ti[0],ti[1],column[1]])
                else:
                    self.info.append([tokenReport.tableInfo[0],tokenReport.tableInfo[1],column[0]])

            return self.info




    #입력된 query의 모든 token을 Recursive하게 찾음
    #token에는 subtoken이 존재한는 경우가 있음
    #subtoken이 존재하지 않은 경우가까지 Recursibe하게 찾아줌
    #Input:
    #   token: extractColumn에서 한번 token화 한 query statment의 하나의 토큰
    #Output:
    #   parsedToken: query statment의 전체 token List
    def parseToken(self, token):
        # if token.ttype == "Token.Keyword":
        tokentype = str(token.ttype)

        if hasattr(token, 'tokens'):
            for subtoken in token.tokens:
                #is_whitespace == FALSE -> query안의 빈칸들은 의미가 없음
                #hasattr(subtoken 'tokens') == FALSE -> token의 leaf에 도달했을
                #경우에만 append. leaf가 아닐경우에는 해당 token을 다시 parseToken
                if subtoken.is_whitespace == False and hasattr(subtoken, 'tokens') == False and str(token.ttype != "Token.Keyword"):
                    self.parsedToken.append(str(subtoken).upper())
                else: self.parseToken(subtoken)
        elif str(token.ttype) == "Token.Keyword":
            self.parsedToken.append(str(token))


# sqlInsert = "INSERT INTO SCHEMA1.TABLE1 (A, B, C, D, E, F, G) VALUES (1,2,3,4,5,6,7);"
# sqlSelect1 = "SELECT c.A FROM SCHEMA1.CITY as c WHERE c.ABC = 1 AND c.TEST2=(SELECT b.A FROM SCHEMA2.BUG as b WHERE (SELECT D.A from schema4.table4 as D where D.C = 1)) AND c.TEST = 1;"
# sqlSelect2 = "SELECT t.A, t1.B, t2.C FROM schema.table as t, schema1.table1 as t1, schema2.table2 as t2 WHERE t.B = 1 AND t.C = 1;"
# sqlUpdate = "UPDATE SCHEMA1.TABLE1 SET A=1, B=2, C=3 WHERE D=1 AND E=(SELECT b.A FROM SCHEMA2.BUG as b WHERE (SELECT D.A from schema4.table4 as D where D.C = 1)) AND F=1;"
# sqlDelete = "DELETE FROM SCHEMA1.TABLE1 WHERE TEST=(SELECT b.A FROM SCHEMA2.BUG as b WHERE (SELECT D.A from schema4.table4 as D where D.C = 1)) and A=1 "
# it = RecursiveTokenParser(sqlInsert)
#ut = RecursiveTokenParser(sqlUpdate)
#st = RecursiveTokenParser(sqlSelect1)
# st2 = RecursiveTokenParser(sqlSelect2)
# dt = RecursiveTokenParser(sqlDelete)
# #print(it.extractColumn())
#print(ut.extractColumn())
#print(st.extractColumn())
# #print(dt.extractColumn())
# #print(st2.extractColumn())
