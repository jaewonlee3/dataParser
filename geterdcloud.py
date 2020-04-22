#!/usr/bin/python3
# encoding=utf-8

print('content-type:text/html; charset=utf-8\n')
print('Hello python!')
print('Parsing SQL from erccloud ...')

import sys
sys.path.insert(0,"/home/yunjy/.local/lib/python3.6/site-packages/selenium")

from selenium import webdriver

try:
    print('chrome_options')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--allow-insecure-localhost");
    chrome_options.add_argument('headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome('./chromedriver/chromedriver_linux64/chromedriver',chrome_options=chrome_options)
    print('driver finished')

    driver.implicitly_wait(1)
    driver.get('https://www.erdcloud.com/login')
    print("driver.get('https://www.erdcloud.com/login')")
    print(driver.page_source.encode('utf-8'))
    driver.find_element_by_id('email').send_keys("계정은 그대만 알려줄게요~ >_<")
    driver.implicitly_wait(10)
    print("id")
    driver.find_element_by_name('password').send_keys('비밀번호도 그대만 따로 알려줄게요~ >_<')
    print("pw")
    print('start to find_element_by_xpath')
    driver.find_element_by_id('log-in-button').click()
    print("find_element_by_xpath")
    print('start to find link_text FS')
    driver.find_element_by_link_text('FS').click()
    print('finished')
    print('start to find class js-btn-export')

    driver.find_element_by_class_name('js-btn-export').click()
    driver.implicitly_wait(2)
    print('finished')
    print('start to find oracle')
    driver.find_element_by_class_name('js-btn-dbSelect').click()
    driver.implicitly_wait(2)
    focused = driver.find_element_by_class_name('db-select-box')
    print(focused.find_elements_by_tag_name('label')[1].get_attribute('id'))
    driver.implicitly_wait(2)
    focused.find_elements_by_tag_name('label')[1].click()

    print('finished')

    print('start to find class js-btn-sql-preview')
    driver.find_element_by_class_name('js-btn-sql-preview').click()
    print('finished')
    print('start to find tag textarea[1]')
    mytext=driver.find_elements_by_tag_name('textarea')[1].get_attribute('value')
    print('finished')

#########################################################
    import cgi
    form = cgi.FieldStorage()
    jsname='sqldata.js'
    print('file opend:'+jsname)
    opened_file = open(jsname, 'w',encoding='utf-8')
    print('start to write')
    try: 
        opened_file.write(mytext)
    except:
        print("!!!!!!!!!!!!!CHECK THE KOREAN TEXT INCLUDDED!!!!!!!!!!!")
    print('finished')
    opened_file.close()
    print('!opened_file.close()!')
    print('SEE:'+jsname+'\n')
    print('EXECUTE:' +'sql2array2d with convert2dtojs'+'\n')
#    from glob import glob
#    nextseq = glob('sql2array2d.py')
#    for seq in nextseq:
#        exec(open(seq).read())
#### sql2array2d #####################################################
    # !/usr/bin/python3
    # -*- coding:utf-8 -*-
    import shutil
    import time

    now = time.localtime()
    s = "%04d%02d%02d_%02d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    jsname = 'sqldata.js'
    shutil.copy(jsname, jsname + s)

    print('file opened:' + jsname)
    f = open(jsname, 'r', encoding='utf-8')

    lines = f.readlines()
    my1d = []
    my1dTable = []
    for line in lines:
        myline = line.replace('\n', '').replace('\t', '===')
        my1d.append(myline)
        if myline.split('TABLE')[0].replace(' ', '') == 'ALTER':
            break
        else:
            my1dTable.append(myline)
#            print(myline)

    print('finished')
    f.close()
    print('!opened_file.close()!')
    my1dTableOnly = []
    for x in my1dTable:
        my1dTableOnly.append(x.replace(');', ''))

    while '' in my1dTableOnly:
        my1dTableOnly.remove('')

#    print(my1d)
#    print(my1dTable)
#    print(my1dTableOnly)
#    for x in my1dTableOnly:
#        print(x)

    my2dTable = []
    for i in range(len(my1dTableOnly)):
        temp = my1dTableOnly[i].split('=')
        while '' in temp:
            temp.remove('')
        my2dTable.append(temp)

    entities = []
    header_idx = 0
    header_name = ""
    my2dTableOnly = []
    for i in range(len(my2dTable)):
        if len(my2dTable[i]) == 1:
            entity = my2dTable[i][0].replace('CREATE TABLE "', '').replace('"', '').replace('(', '').replace(' ', '')
            entities.append(entity)

            header_idx = i
            header_name = entity
        else:
            col = my2dTable[i][0].replace('CREATE TABLE "', '').replace('"', '').replace('(', '').replace(' ', '')
            type = my2dTable[i][1].replace('"', '').replace('(', '').replace(' ', '')
            isnul = my2dTable[i][2].replace('"', '').replace('(', '').replace(',', '').replace(' ', '')
            isnul = isnul.replace('NOTNULL', 'NOT NULL')

            # print(entity, '  |  ', my2dTable[i][0], '  |  ', my2dTable[i][1], '  |  ', my2dTable[i][2],)
#            print('|' + entity + '|' + col + '|' + type + '|' + isnul + '|')
            my2dTableOnly.append([entity, col, type, isnul])
#    print(entities)
#    print(my2dTableOnly)
#    print(len(my2dTableOnly))
    print("--------------------------")
#    for x in my2dTableOnly:
#        print(x)
#    print(len(my2dTableOnly))
    print("--------------------------")

    import convert2dtojs

    varname = 'dataSet_erdcloud'
    jsname = 'dataSet_erdcloud.js'
    convert2dtojs.write2dtojs(my2dTableOnly, varname, jsname)
    
except:
    print("!!!!!!!!!!!!!!!SOMETHING is wrong!!!!!!!!!!!!!!!!")
################################################################

finally:
    print('driver.quit()')
    driver.quit();
    print('!driver.quit()!')










