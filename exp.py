import csv

a = {'aa': [1,23,4,5,6], 'bb': 'dd', 'cc': 'll'}

f = open("C:/Users/이재원/Documents/code/newFile.csv", "w", newline = "")
wr = csv.writer(f)
wr.writerow([1, a['aa'],a['bb']])

f.close()