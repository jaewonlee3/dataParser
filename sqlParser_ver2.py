import sqlparse
from sqlparse.sql import Where, Comparison, Parenthesis, Identifier, IdentifierList


class RecursiveTokenParser(object):
 def __init__(self, query):
    self.query = query
    self.names = []
    self.elements = sqlparse.parse(self.query)
    self.stmt = self.elements[0]
 def extractColumn(self):
     query_type = self.stmt.get_type()
     if self.stmt.get_type() == 'INSERT' :
         print("insert query")
         return self.insert_query()
     else :
        if self.stmt.get_type() == 'SELECT' :
            print("select query")

 def insert_query(self):
    #elements = sqlparse.parse(self.query)
    #print(elements[0].tokens)
    for token in self.stmt.tokens:
        if isinstance(token, Identifier):
            self.identifier(token)
        elif isinstance(token, IdentifierList):
            print(token)
            self.identifier(token)
        elif isinstance(token, Parenthesis):
            self.parenthesis(token)
        elif isinstance(token, Where):
            self.where(token)

    return [str(name).upper() for name in self.names]

 def where(self, token):

    for subtoken in token.tokens:
        if isinstance(subtoken, Comparison):
            self.comparison(subtoken)

 def comparison(self, token):
    for subtoken in token.tokens:
        if isinstance(subtoken, Parenthesis):
            self.parenthesis(subtoken)

 def parenthesis(self, token):

    for subtoken in token.tokens:
        if isinstance(subtoken, Identifier):
            self.identifier(subtoken)
        elif isinstance(subtoken, Parenthesis):
            self.parenthesis(subtoken)

 def identifier(self, token):
    self.names.append(token)

 def identifierList(self, token):
     self.names.append(token)

 def get_query(self):  #
    return self.query

sqlInsert = "INSERT INTO SCHEMA1.TABLE1 (A, B, C, D, E, F, G) VALUES (1,2,3,4,5,6,7)"
sqlSelect = "SELECT a FROM CITY WHERE a = (SELECT e FROM  Country)"
insertTest = RecursiveTokenParser(sqlInsert)
selectTest = RecursiveTokenParser(sqlSelect)
print(insertTest.extractColumn())
print(selectTest.extractColumn())
#print(t.get_query())
#print(t.insert_query())
