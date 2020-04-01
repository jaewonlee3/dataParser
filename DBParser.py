# -*- coding: UTF-8 -*-

import jaydebeapi
import jpype

def DBConn (ip, user, password):
    ip = "jdbc:tibero:thin:@"+ip+":tibero"
    conn = jaydebeapi.connect('com.tmax.tibero.jdbc.TbDriver', ip , driver_args={'user': user, 'password': password}, jars="C:/tibero6-jdbc.jar")
    columnList = []
    db = conn.cursor()
    db.execute("select owner, table_name, column_name, data_type, data_length, nullable from all_tab_columns where owner NOT IN ('SYS' , 'SYSCAT' , 'SYSGIS', 'OUTLN');")
    columnList = db.fetchall()
    db.close
    conn.close
    return columnList

def DBParser (columnList):
    DBList = []
    for columnInfo in columnList:
        DBdict = {}
        DBdict["SCHEMA"] = columnInfo[0]
        DBdict["TABLE"] = columnInfo[1]
        DBdict["COLUMN"]= columnInfo[2]
        DBList.append(DBdict)
    return DBList

if __name__ == '__main__':
    ip = "192.1.4.246:8629"
    rs = DBConn(ip, "sys", "tibero")
    list = DBParser(rs)
    print(list)
