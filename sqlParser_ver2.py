import sqlparse
from sqlparse.sql import Where, Comparison, Parenthesis, Identifier, IdentifierList


class RecursiveTokenParser(object):
    def __init__(self, query):
        self.query = query
        self.names = []
        self.elements = sqlparse.parse(self.query)
        self.stmt = self.elements[0]
        #token 안에 존재하는 whitespace (빈칸) 정리
        for token in self.stmt.tokens:
            if token.is_whitespace:
                self.stmt.tokens.pop(self.stmt.tokens.index(token))


    def extractColumn(self):
         query_type = self.stmt.get_type()
         if query_type == 'INSERT' :
             print("This SQL is a INSERT DML")
             return self.insert_query()
         else:
             query_type == 'SELECT'
             print("This SQL is a SELECT DML")
             return self.select_query()


    def insert_query(self):
        #elements = sqlparse.parse(self.query)
        #print(elements[0].tokens)
        for token in self.stmt.tokens:
            if isinstance(token, Identifier):
                self.identifier(token)
            elif isinstance(token, IdentifierList):
                self.identifier(token)
        return [str(name).upper() for name in self.names]


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
            print(subtoken)
            if isinstance(subtoken, Identifier):
                self.identifier(subtoken)
            elif isinstance(subtoken, Where) :
                self.where(token)
            elif isinstance(subtoken, Parenthesis):
                self.parenthesis(subtoken)


    def identifier(self, token):
        self.names.append(token)

    def identifierList(self, token):
        self.names.append(token)

    def get_query(self):
        return self.query

sqlInsert = "INSERT INTO SCHEMA1.TABLE1 (A, B, C, D, E, F, G) VALUES (1,2,3,4,5,6,7);"
sqlSelect = "SELECT c.A FROM CITY as c WHERE (SELECT B.A FROM BUG as b WHERE b.f = 3);"
it = RecursiveTokenParser(sqlInsert)
st = RecursiveTokenParser(sqlSelect)
print(it.extractColumn())
print(st.extractColumn())
#print(t.get_query())
#print(t.insert_query())
