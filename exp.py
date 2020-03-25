
a = 'http://192.168.156.156:14000\FS/JJ\ReadDepartment?action=SO'
c = a.split('/')
for k in c:
    b = k.split('\\')
    for j in b:
        print('--------------')
        print(j)
