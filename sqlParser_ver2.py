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
        #token 안에 존재하는 whitespace (빈칸) 정리
        for token in self.stmt.tokens:
            if token.is_whitespace:
                self.stmt.tokens.pop(self.stmt.tokens.index(token))
                if isinstance(token, (Parenthesis, Comparison, Where)):
                    for subtoken in token.tokens:
                        if subtoken.is_whitespace:
                            subtokenIndex = token.tokens.index(subtoken)
                            token.tokens.pop(subtokenIndex)
    def extractColumn(self):
         query_type = self.stmt.get_type()
         if query_type == 'INSERT' :
             print("This SQL is a INSERT DML")
             return self.insert_query()
         elif query_type == 'SELECT':
             print("This SQL is a SELECT DML")
             return self.select_query()
         elif query_type == 'UPDATE' :
             print("This SQL is a UPDATE DML")
             return self.update_query()


    #insert쿼리문 처리
    def insert_query(self):
        #elements = sqlparse.parse(self.query)
        #print(elements[0].tokens)
        for token in self.stmt.tokens:
            if isinstance(token, Identifier):
                self.identifier(token)
            elif isinstance(token, IdentifierList):
                self.identifier(token)
        for name in self.names:
            # print(name)
            if str(name) == '.':
                periodIndex =  self.names.index(name)
                schemaName = str(self.names[periodIndex-1])
                tableString = str(self.names[periodIndex+1])
                tableString = tableString.replace(")","")
        tableInfo = tableString.split("(")
        tableName = tableString.split("(")[0]
        tableColumns = tableString.split("(")[1].split(",")
        for tableColumn in tableColumns:
            self.info.append([schemaName, tableName, tableColumn])

        return self.info


    def update_query(self):
        for token in self.stmt.tokens:
            # print(str(token)+": "+str(token.ttype))
            if isinstance(token, Identifier):
                self.identifier(token)
            elif isinstance(token, IdentifierList):
                self.identifier(token)
            elif isinstance(token, Parenthesis):
                self.parenthesis(token)
            elif isinstance(token, Where):
                self.where(token)
        for name in self.names:
            print(name)
            if str(name) == '.':
                periodIndex =  self.names.index(name)
                schemaName = str(self.names[periodIndex-1])
                tableName = str(self.names[periodIndex+1])
        print(schemaName)
        print(tableName)

        # tableInfo = tableString.split("(")
        # tableName = tableString.split("(")[0]
        # tableColumns = tableString.split("(")[1].split(",")
        # for tableColumn in tableColumns:
        #     self.info.append([schemaName, tableName, tableColumn])
        #
        # return self.info
    def select_query(self):
        for token in self.stmt.tokens:
            if isinstance(token, Identifier):
                self.identifier(token)
            elif isinstance(token, IdentifierList):
                self.identifier(token)
            elif isinstance(token, Parenthesis):
                self.parenthesis(token)
            elif isinstance(token, Where):
                self.where(token)
        return [str(name).upper() for name in self.names]

    def where(self, token):
        for subtoken in token.tokens:
            # print("where: "+str(subtoken)+" "+str(subtoken.ttype))
            if isinstance(subtoken, Comparison):
                self.comparison(subtoken)
            elif isinstance(subtoken, Parenthesis):
                self.parenthesis(subtoken)
            elif isinstance(subtoken, Where):
                self.where(subtoken)


    def comparison(self, token):
        for subtoken in token.tokens:

            if isinstance(subtoken, Parenthesis):
                self.parenthesis(subtoken)
            elif isinstance(subtoken, Identifier):
                self.identifier(subtoken)

    def parenthesis(self, token):
        for subtoken in token.tokens:
            # print("para:" + str(subtoken)+" "+str(subtoken.ttype))
            if isinstance(subtoken, Identifier):
                self.identifier(subtoken)
            elif isinstance(subtoken, Where) :
                 self.where(token)
            elif isinstance(subtoken, Parenthesis):
                self.parenthesis(subtoken)


    def identifier(self, token):
        for subtoken in token.tokens:
            self.names.append(subtoken)

    def identifierList(self, token):
        for subtoken in token.tokens:
            self.names.append(subtoken)

    def get_query(self):
        return self.query

sqlInsert = "INSERT INTO SCHEMA1.TABLE1 (A, B, C, D, E, F, G) VALUES (1,2,3,4,5,6,7);"
sqlSelect = "SELECT c.A FROM CITY as c WHERE (SELECT B.A FROM BUG as b WHERE b.f = 3);"
sqlUpdate = "UPDATE SCHEMA1.TABLE1 SET A=1, B=2, C=3 WHERE D=1"
it = RecursiveTokenParser(sqlInsert)
ut = RecursiveTokenParser(sqlUpdate)
#st = RecursiveTokenParser(sqlSelect)
print(it.extractColumn())
print(ut.extractColumn())
#print(st.extractColumn())
#print(t.get_query())
#print(t.insert_query())
