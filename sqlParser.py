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
         query_type = self.stmt.get_type()
         print("This is a "+ query_type+" query")
         for token in self.stmt.tokens:
             self.parseToken(token)
         return self.tokenReport(query_type, self.parsedToken)


    #Query Analyser
    def tokenReport(self, query_type, parsedToken):
        #insert 쿼리 분석
        #insert 쿼리 형태:
        #   INSERT INTO SCHEMA.TABLE (컬럼 정보) VALUE (값 정보)
        if query_type == "INSERT":
            # insert 쿼리의 시작은 항상 (INSERT) INTO SCHEMA.TABLE이기 때문에
            # 1,3 번 인덱스로 스키마랑 테이블 이름 추출
            schemaName = parsedToken[1]
            tableName = parsedToken[3]
            # 스키마,테이블은 사용했으니 다음 iter에서 빼서 돌린다.
            for token in parsedToken[4:]:
                #컬럼 이름 정보 빼고는 관심이 없기때문에 예외처리로 걸러낸다
                if token == "(" or token == ",":
                    continue
                #insert 쿼리에서 VALUE (값 정보)는 필요없어서 첫 ()이 끝나는
                #시점으로 break를 해준다
                elif token == ")":
                    break
                #위에 명시된 예외처리 된 내용이 아니라면 컬럼 정보
                #self.info에 담는다
                else:
                    self.info.append([schemaName, tableName, token])
            return self.info

        #update 쿼리 분석
        #update 쿼리 형태:
        #   UPDATE SCHEMA.TABLE SET 컬럼정보1,컬럼정보2,....컬럼정보N WHERE -> 컬럼정보
        #                                                             ㄴ> 서브쿼리 정보
        elif query_type == "UPDATE":
            for index, token in enumerate(parsedToken):
                #update 쿼리는 UPDATE 다음 무조건 스키마 이름. 테이블 이름 형태
                # 0,2 인덱스로 추출
                schemaName = parsedToken[0]
                tableName = parsedToken[2]
                whereCount = 0
                subqueryCount = 0
                #컬럼 정보는 컬럼이름 = 값 형태임으로 "=" 앞의 정보로 컬럼이름 추출
                if token == "=":
                    columnInfo = [schemaName,tableName,parsedToken[index-1]]
                    if columnInfo not in self.info:
                        self.info.append(columnInfo)
                #WHERE 후에는 두가지 가능성 존재
                #   1. 컬럼 정보: 컬럼이름 = 값
                #      "="를 찾아서 위랑 똑같이 처리한다
                #   2. Subquery 정보: (SELECT QUERY)
                #       괄호 사이의 정보를 추출해서 tokenReport로 SELECT 형태로 다시 돌린다
                elif token == "WHERE" and whereCount == 0:
                    whereCount += 1
                    tokenWhereEnd = parsedToken[index:]
                    # print(tokenWhereEnd)
                    for subindex, token in enumerate(tokenWhereEnd):
                        if token == "(":
                            subqueryCount += 1
                            if subqueryCount == 1:
                                tokenSubQuery = tokenWhereEnd[subindex+1:]
                                self.tokenReport("SELECT", tokenSubQuery)
                            elif token == ")":
                                subqueryCount -=1

            return self.info

        elif query_type == "DELETE":
            whereCount = 0
            subqueryCount = 0
            schemaName = parsedToken[1]
            tableName = parsedToken[3]
            for index, token in enumerate(parsedToken):
                if token == "WHERE" and whereCount == 0:
                    whereCount += 1
                    tokenWhereEnd = parsedToken[index:]
                    for subindex, token in enumerate(tokenWhereEnd):
                        if token == "(":
                            subqueryCount += 1
                            if subqueryCount == 1:
                                tokenSubQuery = tokenWhereEnd[subindex+1:]
                                self.tokenReport("SELECT", tokenSubQuery)
                        elif token == "=" and subqueryCount == 0:
                            columnInfo = [schemaName,tableName,tokenWhereEnd[subindex-1]]
                            if columnInfo not in self.info:
                                self.info.append(columnInfo)
                        elif token == ")":
                            subqueryCount -= 1

            return self.info

        elif query_type == "SELECT" :
            tableInfo = []
            columnName = []
            for index, token in enumerate(parsedToken):
                if token == "FROM":
                    tokenStartFrom = parsedToken[:index]
                    for subindex, token in enumerate(tokenStartFrom):
                        if token == ".":
                            columnName.append([parsedToken[subindex-1], parsedToken[subindex+1]])
                    tokenFromEnd = parsedToken[index:]
                    for subindex, token in enumerate(tokenFromEnd):
                        if token == "AS":
                            tableInfo.append([tokenFromEnd[subindex-3],tokenFromEnd[subindex-1],tokenFromEnd[subindex+1]])
                        elif token == "WHERE":
                            break
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
                        if tableAlias == ti[2]:
                            columnInfo = [ti[0],ti[1],column[1]]
                            if columnInfo not in self.info:
                                self.info.append([ti[0],ti[1],column[1]])
                else:
                    self.info.append([tokenReport.tableInfo[0],tokenReport.tableInfo[1],column[0]])

            return self.info




    #모든 토큰을 Recursive하게 찾음
    def parseToken(self, token):
        # if token.ttype == "Token.Keyword":
        tokentype = str(token.ttype)

        if hasattr(token, 'tokens'):
            for subtoken in token.tokens:
                if subtoken.is_whitespace == False and hasattr(subtoken, 'tokens') == False and str(token.ttype != "Token.Keyword"):
                    self.parsedToken.append(str(subtoken).upper())
                else: self.parseToken(subtoken)
        elif str(token.ttype) == "Token.Keyword":
            self.parsedToken.append(str(token))


sqlInsert = "INSERT INTO SCHEMA1.TABLE1 (A, B, C, D, E, F, G) VALUES (1,2,3,4,5,6,7);"
sqlSelect1 = "SELECT c.A FROM SCHEMA1.CITY as c WHERE c.ABC = 1 AND c.TEST2=(SELECT b.A FROM SCHEMA2.BUG as b WHERE (SELECT D.A from schema4.table4 as D where D.C = 1)) AND c.TEST = 1;"
sqlSelect2 = "SELECT t.A, t1.B, t2.C FROM schema.table as t, schema1.table1 as t1, schema2.table2 as t2 WHERE t.B = 1 AND t.C = 1;"
sqlUpdate = "UPDATE SCHEMA1.TABLE1 SET A=1, B=2, C=3 WHERE D=1 AND E=(SELECT b.A FROM SCHEMA2.BUG as b WHERE (SELECT D.A from schema4.table4 as D where D.C = 1)) AND F=1;"
sqlDelete = "DELETE FROM SCHEMA1.TABLE1 WHERE TEST=(SELECT b.A FROM SCHEMA2.BUG as b WHERE (SELECT D.A from schema4.table4 as D where D.C = 1)) and A=1 "
# it = RecursiveTokenParser(sqlInsert)
ut = RecursiveTokenParser(sqlUpdate)
st = RecursiveTokenParser(sqlSelect1)
# st2 = RecursiveTokenParser(sqlSelect2)
# dt = RecursiveTokenParser(sqlDelete)
# print(it.extractColumn())
print(ut.extractColumn())
print(st.extractColumn())
# print(dt.extractColumn())
# print(st2.extractColumn())
