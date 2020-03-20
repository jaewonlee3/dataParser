## -*- coding: UTF-8 -*-

import sqlparse
from sqlparse.sql import Where, Comparison, Parenthesis, Identifier, IdentifierList
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
         for token in self.stmt.tokens:
             self.parseToken(token)
         return self.tokenReport(query_type)


    #Query Analyser
    def tokenReport(self, query_type):
        if query_type == "INSERT":
            print("INSERT QUERY")
            schemaName = self.parsedToken[1]
            tableName = self.parsedToken[3]
            for token in self.parsedToken[4:]:
                if token == "(" or token == ",":
                    continue
                elif token == ")" :
                    break
                else:
                    self.info.append([schemaName, tableName, token])
            return self.info
        if query_type == "UPDATE" :
            print("UPDATE QUERY")
            schemaName = self.parsedToken[0]
            tableName = self.parsedToken[2]
            aftercomparison = "0"
            for token in self.parsedToken[3:]:
                if aftercomparison == "1":
                    aftercomparison = "0"
                    continue
                elif token == "SET" or token == "," or token == "WHERE" or token == ";":
                    continue
                elif token == "(":
                    print("subquery area")
                elif token == "=" :
                    aftercomparison = "1"
                else:
                    self.info.append([schemaName,tableName,token])
            return self.info

        if query_type == "DELETE":
            print("DELETE QUERY")
            schemaName = self.parsedToken[1]
            tableName = self.parsedToken[3]
            whereCount = 0
            aftercomparison = 0
            for token in self.parsedToken[4:]:
                if token == "." or token == "," or aftercomparison == "1" or token == "AND":
                    aftercomparison = 0
                    continue
                elif token == "WHERE":
                    whereCount = 1
                    continue
                elif token == "=":
                    aftercomparison = "1"
                    continue
                if whereCount == 1 and token == "(":
                    print("subquery area")
                else:
                    self.info.append([schemaName,tableName,token])
                    whereCount = 0
        return self.info
        if query_type == "SELECT" :
            print("SELECT QUERY")
            print("select query area")




    #모든 토큰을 Recursive하게 찾음
    def parseToken(self, token):
        # if token.ttype == "Token.Keyword":
        tokentype = str(token.ttype)

        if hasattr(token, 'tokens'):
            for subtoken in token.tokens:
                if subtoken.is_whitespace == False and hasattr(subtoken, 'tokens') == False and str(token.ttype != "Token.Keyword"):
                    self.parsedToken.append(str(subtoken))
                else: self.parseToken(subtoken)
        elif str(token.ttype) == "Token.Keyword":
            self.parsedToken.append(str(token))
            # else: self.parsedToken.append(str(token))
        #insert쿼리문 처리
        # # OLD VERSION
        # def insert_query(self):
        #     #elements = sqlparse.parse(self.query)
        #     #print(elements[0].tokens)
        #     for token in self.stmt.tokens:
        #         self.parseToken(token)
        #         if isinstance(token, Identifier):
        #             self.identifier(token)
        #         elif isinstance(token, IdentifierList):
        #             self.identifier(token)
        #     for name in self.names:
        #         schemaName = str(name).split(".")[0]
        #         tableName = str(name).split(".")[1].split("(")[0]
        #         tableColumns = str(name).split(".")[1].split("(")[1]
        #         tableColumns = tableColumns.replace(" ","")
        #         tableColumns = tableColumns.replace(")","")
        #         tableColumns = tableColumns.split(",")
        #     for tableColumn in tableColumns:
        #         self.info.append([schemaName, tableName, tableColumn])
        #     return self.info
        # def insert_query(self):
        #     for token in self.stmt.tokens:
        #         self.parseToken(token)
        #     return self.tokenReport(self.stmt.get_type())
        #
        #update 쿼리문 처리
        ## OLD VERSION
        # def update_query(self):
        #     print(self.stmt.tokens)
        #     for token in self.stmt.tokens:
        #         print(str(token)+": "+str(token.ttype))
        #         if isinstance(token, Identifier):
        #             self.identifier(token)
        #         elif isinstance(token, IdentifierList):
        #             self.identifier(token)
        #         elif isinstance(token, Parenthesis):
        #             self.parenthesis(token)
        #         elif isinstance(token, Where):
        #             self.where(token)
        #     print([str(name).upper() for name in self.names])
        #
        #     for name in self.names:
        #         print(name)
        #         if str(name) == '.':
        #             periodIndex =  self.names.index(name)
        #             schemaName = str(self.names[periodIndex-1])
        #             tableName = str(self.names[periodIndex+1])
        #     print(schemaName)
        #     print(tableName)
        #
        #     tableInfo = tableString.split("(")
        #     tableName = tableString.split("(")[0]
        #     tableColumns = tableString.split("(")[1].split(",")
        #     for tableColumn in tableColumns:
        #         self.info.append([schemaName, tableName, tableColumn])
        #
        #     return self.info
        # def update_query(self):
        #     for token in self.stmt.tokens:
        #         self.parseToken(token)
        #     return self.tokenReport(self.stmt.get_type())
        # def select_query(self):
        #     for token in self.stmt.tokens:
        #         if isinstance(token, Identifier):
        #             self.identifier(token)
        #         elif isinstance(token, IdentifierList):
        #             self.identifier(token)
        #         elif isinstance(token, Parenthesis):
        #             self.parenthesis(token)
        #         elif isinstance(token, Where):
        #             self.where(token)
        #     return [str(name).upper() for name in self.names]
    # def where(self, token):
    #     for subtoken in token.tokens:
    #         # print("where: "+str(subtoken)+" "+str(subtoken.ttype))
    #         if isinstance(subtoken, Comparison):
    #             self.comparison(subtoken)
    #         elif isinstance(subtoken, Parenthesis):
    #             self.parenthesis(subtoken)
    #         elif isinstance(subtoken, Where):
    #             self.where(subtoken)
    #
    #
    # def comparison(self, token):
    #     for subtoken in token.tokens:
    #
    #         if isinstance(subtoken, Parenthesis):
    #             self.parenthesis(subtoken)
    #         elif isinstance(subtoken, Identifier):
    #             self.identifier(subtoken)
    #
    # def parenthesis(self, token):
    #     for subtoken in token.tokens:
    #         # print("para:" + str(subtoken)+" "+str(subtoken.ttype))
    #         if isinstance(subtoken, Identifier):
    #             self.identifier(subtoken)
    #         elif isinstance(subtoken, Where) :
    #              self.where(token)
    #         elif isinstance(subtoken, Parenthesis):
    #             self.parenthesis(subtoken)
    #
    #
    # def identifier(self, token):
    #     self.names.append(token)
    #     # for subtoken in token.tokens:
    #     #     self.names.append(subtoken)
    #
    # def identifierList(self, token):
    #     for subtoken in token.tokens:
    #         self.names.append(subtoken)
    #
    # def get_query(self):
    #     return self.query

sqlInsert = "INSERT INTO SCHEMA1.TABLE1 (A, B, C, D, E, F, G) VALUES (1,2,3,4,5,6,7);"
sqlSelect = "SELECT c.A FROM CITY as c WHERE (SELECT B.A FROM BUG as b WHERE b.f = 3);"
sqlUpdate = "UPDATE SCHEMA1.TABLE1 SET A=1, B=2, C=3 WHERE D=1;"
sqlDelete = "DELETE FROM SCHEMA1.TABLE1 WHERE A=1 AND B=2"
it = RecursiveTokenParser(sqlInsert)
ut = RecursiveTokenParser(sqlUpdate)
st = RecursiveTokenParser(sqlSelect)
dt = RecursiveTokenParser(sqlDelete)
print(it.extractColumn())
print(ut.extractColumn())
print(st.extractColumn())
print(dt.extractColumn())
print(it.parsedToken)
print(ut.parsedToken)
print(st.parsedToken)
print(dt.parsedToken)
# print(ut.extractColumn())
# print(it.parsedToken)
#print(st.extractColumn())
#print(t.get_query())
#print(t.insert_query())
