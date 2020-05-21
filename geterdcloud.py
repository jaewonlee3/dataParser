#!/usr/bin/python3
# encoding=utf-8

print('content-type:text/html; charset=utf-8\n')
print('Hello python!')
print('Parsing SQL from erccloud ...')

import sys
sys.path.insert(0,"/home/yunjy/.local/lib/python3.6/site-packages/selenium")

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pyautogui
import cgi

# "sangwan_kim@tmax.co.kr" 'tmaxbi32'

def getErdCloud(mail, password, app):
    try:
        print('chrome_options')
        chrome_options = webdriver.ChromeOptions()
        # 창을 띄우지 않고 크롬을 사용하는 옵션
        chrome_options.add_argument('--headless')
        # 웹페이지 오류 안나게 하는 옵션
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # localhost에서 로드된 리소스에 대해 유효하지 않은 인증서 허용
        chrome_options.add_argument("--allow-insecure-localhost");
        # 크롬을 창을 띄우지 않고 쓰겠다.
        chrome_options.add_argument('headless')
        # 윈도우 해상도를 현재 해상도에 맞춤
        chrome_options.add_argument('window-size=1920x1080')
        # 크롬이 GPU 가속을 사용하다가 버그가 일어나는 현상을 막기 위함
        chrome_options.add_argument("disable-gpu")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        # 크롬 드라이버의 위치 및 옵션 지정 (전체 서버에 맞게 변경 필요)
        driver = webdriver.Chrome('C:/jaewon/chromedriver_win32/chromedriver.exe', chrome_options=chrome_options)
        print('driver finished')

        driver.implicitly_wait(1)
        # erdcloud 사이트 접속
        driver.get('https://www.erdcloud.com/login')
        print("driver.get('https://www.erdcloud.com/login')")
        print(driver.page_source.encode('utf-8'))
        # erdcloud 로그인 -> id, password를 입력받는 형식으로 바꾸기
        driver.find_element_by_id('email').send_keys(mail)
        driver.implicitly_wait(10)
        print("id")
        driver.find_element_by_name('password').send_keys(password)
        print("pw")
        print('start to find_element_by_xpath')
        driver.find_element_by_id('log-in-button').click()
        print("find_element_by_xpath")
        print('start to find link_text FS')
        # 스크롤을 내려야 함
        print("ssss")
        time.sleep(5)
        body = driver.find_element_by_css_selector('html');
        # 스크롤을 내려야 함
        print("kkkk")
        for i in range(10):
            driver.find_element_by_class_name('show-more-box').click();
            time.sleep(1)
            print("scroll down")

        # FS라는 텍스트를 가진 링크를 찾아서 클릭 -> FS는 input해서 찾는 것으로 변환
        driver.find_element_by_link_text(app).click()
        print('finished')
        print('start to find class js-btn-export')

        # class 이름이 js-btn-export인 클래스 찾아서 클릭 (export 버튼 찾아서 클릭)
        driver.find_element_by_class_name('js-btn-export').click()
        driver.implicitly_wait(2)
        print('finished')
        print('start to find oracle')
        # class 이름이 js-btn-dbSelect인 클래스를 클릭 (DB 종류 찾기)
        driver.find_element_by_class_name('js-btn-dbSelect').click()
        driver.implicitly_wait(2)
        # db select box인 클래스를 찾은 후 label 중에 두번째를 클릭 (db 종류를 오라클로 변환)
        focused = driver.find_element_by_class_name('db-select-box')
        print(focused.find_elements_by_tag_name('label')[1].get_attribute('id'))
        driver.implicitly_wait(2)
        focused.find_elements_by_tag_name('label')[1].click()

        print('finished')

        print('start to find class js-btn-sql-preview')
        # js-btn-sql-preview인 클래스를 찾은 후 클릭 (sql preview 버튼 클릭_
        driver.find_element_by_class_name('js-btn-sql-preview').click()
        print('finished')
        print('start to find tag textarea[1]')
        # sql이 들어가있는 textarea를 찾고, 값을 모두 가져옴
        mytext = driver.find_elements_by_tag_name('textarea')[1].get_attribute('value')
        print('finished')
    except:
        print("!!!!!!!!!!!!!!!SOMETHING is wrong!!!!!!!!!!!!!!!!")
        mytext = "wrong"
    finally:
        print('driver.quit()')
        # driver.quit();
        print('!driver.quit()!')
    return mytext

#########################################################
    # cgi -> common gateway interface
    # 받아온 텍스트를 js 파일로 저장
def storeText (mytext):
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

# 이 밑은 erd Parser와 관련된 부분
#     import shutil
#     import time
#
#     now = time.localtime()
#     s = "%04d%02d%02d_%02d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
#     jsname = 'sqldata.js'
#     shutil.copy(jsname, jsname + s)
#
#     print('file opened:' + jsname)
#     f = open(jsname, 'r', encoding='utf-8')
#
#     lines = f.readlines()
#     my1d = []
#     my1dTable = []
#     for line in lines:
#         myline = line.replace('\n', '').replace('\t', '===')
#         my1d.append(myline)
#         if myline.split('TABLE')[0].replace(' ', '') == 'ALTER':
#             break
#         else:
#             my1dTable.append(myline)
# #            print(myline)
#
#     print('finished')
#     f.close()
#     print('!opened_file.close()!')
#     my1dTableOnly = []
#     for x in my1dTable:
#         my1dTableOnly.append(x.replace(');', ''))
#
#     while '' in my1dTableOnly:
#         my1dTableOnly.remove('')
#
# #    print(my1d)
# #    print(my1dTable)
# #    print(my1dTableOnly)
# #    for x in my1dTableOnly:
# #        print(x)
#
#     my2dTable = []
#     for i in range(len(my1dTableOnly)):
#         temp = my1dTableOnly[i].split('=')
#         while '' in temp:
#             temp.remove('')
#         my2dTable.append(temp)
#
#     entities = []
#     header_idx = 0
#     header_name = ""
#     my2dTableOnly = []
#     for i in range(len(my2dTable)):
#         if len(my2dTable[i]) == 1:
#             entity = my2dTable[i][0].replace('CREATE TABLE "', '').replace('"', '').replace('(', '').replace(' ', '')
#             entities.append(entity)
#
#             header_idx = i
#             header_name = entity
#         else:
#             col = my2dTable[i][0].replace('CREATE TABLE "', '').replace('"', '').replace('(', '').replace(' ', '')
#             type = my2dTable[i][1].replace('"', '').replace('(', '').replace(' ', '')
#             isnul = my2dTable[i][2].replace('"', '').replace('(', '').replace(',', '').replace(' ', '')
#             isnul = isnul.replace('NOTNULL', 'NOT NULL')
#
#             # print(entity, '  |  ', my2dTable[i][0], '  |  ', my2dTable[i][1], '  |  ', my2dTable[i][2],)
# #            print('|' + entity + '|' + col + '|' + type + '|' + isnul + '|')
#             my2dTableOnly.append([entity, col, type, isnul])
# #    print(entities)
# #    print(my2dTableOnly)
# #    print(len(my2dTableOnly))
#     print("--------------------------")
# #    for x in my2dTableOnly:
# #        print(x)
# #    print(len(my2dTableOnly))
#     print("--------------------------")
#
#     import convert2dtojs
#
#     varname = 'dataSet_erdcloud'
#     jsname = 'dataSet_erdcloud.js'
#     convert2dtojs.write2dtojs(my2dTableOnly, varname, jsname)
    

################################################################

mytext = getErdCloud("sangwan_kim@tmax.co.kr", 'tmaxbi32', 'FS')
storeText(mytext)











