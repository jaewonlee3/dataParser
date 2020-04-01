# -*- coding: UTF-8 -*-

import jaydebeapi
import jpype

conn = jaydebeapi.connect('com.tmax.tibero.jdbc.TbDriver', 'jdbc:tibero:thin:@192.1.4.246:8629:tibero', driver_args={'user': "sys", 'password': "tibero"}, jars="C:/tibero6-jdbc.jar")
columnList = []
db = conn.cursor()
db.execute("select owner, table_name, column_name, data_type, data_length, nullable from all_tab_columns where owner NOT IN ('SYS' , 'SYSCAT' , 'SYSGIS', 'OUTLN');")
columnList = db.fetchall()
db.close
conn.close
DBList = []
for columnInfo in columnList:
    DBdict = {}
    DBdict["SCHEMA"] = columnInfo[0]
    DBdict["TABLE"] = columnInfo[1]
    DBdict["COLUMN"]= columnInfo[2]
    DBList.append(DBdict)
