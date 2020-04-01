import csv
import ast
import pickle
import utilFunc
import pprint



with open('C:/Users/이재원/Documents/code/Sodict.txt','r', encoding="UTF-8") as inf:
    aa = inf.read()
    dicList = []
    tokenNum = 0
    newData = ""
    for i in aa:
        if i == '{':
            newData = ""
            tokenNum = tokenNum + 1
            newData = newData + i
        elif i == '}':
            tokenNum = tokenNum - 1
            newData = newData + i
            dicList.append(newData)
        else:
            newData = newData + i
    for num, value in enumerate(dicList) :
        dicData = ast.literal_eval(value)
        dicList[num] = dicData
        print(dicData['DEPTH 0'])




