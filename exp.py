import csv
import ast


with open('C:/Users/이재원/Documents/code/PoParserOutput.txt', 'r', encoding='UTF-8') as f:
    mylist = ast.literal_eval(f.read())

for k in mylist:
    print(k)
    print('-----------------')


