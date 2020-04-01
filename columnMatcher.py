
def matchQueryandDB(totalList,dbList):
    for row in totalList:
        tableName = row['TABLE']
        columnName = row['COLUMN']
        for columnInfo in dbList:
            if tableName == columnInfo['TABLE'] and columnName == columnInfo['COLUMN']:
                row["QUERY2DB"] = "Y"
                break
            else:
                row["QUERY2DB"] = "N"
    return totalList

def matchQueryandERD(totalList,ERDList):
    for row in totalList:
        tableName = row['TABLE']
        columnName = row['COLUMN']
        for table in ERDList:
            if tableName in table['TABLE']:
                if columnName in table['COLUMN']:
                    row["QUERY2ERD"] = "Y"
                    break
            else:
                row["QUERY2ERD"] = "N"
    return totalList

    
if __name__ == '__main__' :
    ERDList = [{'TABLE': 'TESTT1', 'COLUMN': ['TESTC1', 'TESTC12', 'TESTC13', 'TESTC11']},
    {'TABLE': 'TESTT2', 'COLUMN': ['TESTC2', 'TESTC22', 'TESTC23']},
    {'TABLE': 'TESTT3', 'COLUMN': ['TESTC4', 'TESTC42']}]
    dbList = [
    {'SCHEMA': 'SL', 'TABLE': 'TESTT1', 'COLUMN': 'TESTC1'},
     {'SCHEMA': 'SL', 'TABLE': 'TESTT2', 'COLUMN': 'TESTC2'},
     {'SCHEMA': 'SL', 'TABLE': 'TESTT3', 'COLUMN': 'TESTC2'}
     ]
    totalList =  [
                {
                    "APPLICATION_NAME": "FS",
                    "SERVICEGROUP_NAME": "CORE",
                    "META": "meta",
                    "DEPTH 0": "com",
                    "DEPTH 1": "tmax",
                    "DEPTH 2": "fs",
                    "DEPTH 3": "client",
                    "DEPTH 4": "type",
                    "DEPTH 5": "so",
                    "SO_NAME": "DeleteClientType",
                    "BO_NAME": "ClientTypeBO",
                    "METHOD_NAME": "deleteClientType",
                    "DOF_NAME": "ClientTypeDOF",
                    "QUERY_NAME": "DELETE",
                    "QUERY": "DELETE FROM FS.CLIENTTYPE WHERE CLIENTTYPE_CODE = :CLIENTTYPE_CODE AND (COMPANY_CODE IS NULL OR COMPANY_CODE = :COMPANY_CODE)",
                    "SCHEMA": "FS",
                    "TABLE": "TESTT1",
                    "COLUMN": "TESTC1"
                },
                {
                    "APPLICATION_NAME": "FS",
                    "SERVICEGROUP_NAME": "CORE",
                    "META": "meta",
                    "DEPTH 0": "com",
                    "DEPTH 1": "tmax",
                    "DEPTH 2": "fs",
                    "DEPTH 3": "client",
                    "DEPTH 4": "type",
                    "DEPTH 5": "so",
                    "SO_NAME": "InsertClientType",
                    "BO_NAME": "ClientTypeBO",
                    "METHOD_NAME": "insertClientType",
                    "DOF_NAME": "ClientTypeDOF",
                    "QUERY_NAME": "INSERT",
                    "QUERY": "INSERT INTO FS.CLIENTTYPE VALUES (:CLIENTTYPE_CODE, :CLIENTTYPE_NAME, :COMPANY_CODE)",
                    "SCHEMA": "FS",
                    "TABLE": "TESTT2",
                    "COLUMN": "TESTC2"
                },
                {
                    "APPLICATION_NAME": "FS",
                    "SERVICEGROUP_NAME": "CORE",
                    "META": "meta",
                    "DEPTH 0": "com",
                    "DEPTH 1": "tmax",
                    "DEPTH 2": "fs",
                    "DEPTH 3": "client",
                    "DEPTH 4": "type",
                    "DEPTH 5": "so",
                    "SO_NAME": "InsertClientType",
                    "BO_NAME": "ClientTypeBO",
                    "METHOD_NAME": "insertClientType",
                    "DOF_NAME": "ClientTypeDOF",
                    "QUERY_NAME": "INSERT",
                    "QUERY": "INSERT INTO FS.CLIENTTYPE VALUES (:CLIENTTYPE_CODE, :CLIENTTYPE_NAME, :COMPANY_CODE)",
                    "SCHEMA": "FS",
                    "TABLE": "TESTT3",
                    "COLUMN": "TESTC3"
                }]

    rs = matchQueryandDB(totalList,dbList)
    rs2 = matchQueryandERD(rs,ERDList)
    print(rs2)
