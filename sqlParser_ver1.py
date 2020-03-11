import sqlparse as sp
from sqlparse.sql import Where, Comparison, Parenthesis, Identifier

sql = "select column1, column2 from schema1.name1"
sqlFormatted = sp.format(sql, reindent=True, keyword_case ='upper')
parsed = sp.parse(sqlFormatted)
# print(sqlParsed[0])
#print(parsed[0].tokens[2])
stmt = parsed[0]
columns = []
for token in stmt.tokens:
    if isinstance(token, Identifier) :
                columns.append(str())
print(columns)
