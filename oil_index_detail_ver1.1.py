#!/usr/bin/python
# -*- coding: utf-8 -*-
#Author: Selvaria
#实时原油指数汇总,各类线 wti，布伦特，上交所
#https://finance.sina.com.cn/futures/quotes/CL.shtml

import requests
import re
from selenium import webdriver
import time
import pymysql
import datetime
import concurrent.futures

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }

def foreign_data(code,name): #当天国外对应期货编号期货值
    url = 'http://hq.sinajs.cn/?_=/&list=hf_'+ code
    url_page = requests.get(url, headers = headers).text
    pattern_str = re.compile('"(.*)"') #获取双引号内的内容
    str_data = pattern_str.findall(url_page)[0]
    data_split = str_data.split(',')
    #print(data_split)
    real = data_split[0]
    open_price = data_split[8]
    high = data_split[4]
    low = data_split[5]
    yesterday = data_split[7]
    #deal_num = data_split[14]
    date = data_split[-2]
    data_row = [name, code, real, yesterday, open_price, high, low]
    return data_row

def futures_data(code,name): #当天国内对应期货编号期货值           
    url = 'http://hq.sinajs.cn/?_=/&list='+ code
    url_page = requests.get(url, headers = headers).text
    #print(url_page)
    #print(type(url_page))
    pattern_str = re.compile('"(.*)"') #获取双引号内的内容
    str_data = pattern_str.findall(url_page)[0]
    data_split = str_data.split(',')
    #print(data_split)
    real = data_split[7]
    open_price = data_split[2]
    high = data_split[3]
    low = data_split[4]
    yesterday = data_split[10]
    deal_num = data_split[14]
    date = data_split[17]
    close = data_split[8]
    data_row = [name,code, real, yesterday, open_price, high, low, close] #'编号','实际价','昨结算','开盘价','最高价','最低价','收盘价'
    return data_row


#日K当天

#CHROME_OPTIONS = webdriver.ChromeOptions()
#CHROME_OPTIONS.add_argument('headless')
#browser = webdriver.Chrome(chrome_options=CHROME_OPTIONS)
browser = webdriver.PhantomJS()
#browser = webdriver.Chrome()

def futures_data(code='SC0', name='原油SC0'): #当天国内对应期货编号期货各项值           
    url = 'http://hq.sinajs.cn/?_=/&list='+ code
    url_page = requests.get(url, headers = headers).text
    #print(url_page)
    #print(type(url_page))
    pattern_str = re.compile('"(.*)"') #获取双引号内的内容
    str_data = pattern_str.findall(url_page)[0]
    data_split = str_data.split(',')
    #print(data_split)
    real = data_split[7]
    open_price = data_split[2]
    high = data_split[3]
    low = data_split[4]
    yesterday = data_split[10]
    deal_num = data_split[14]
    #local_date = data_split[17]
    close = data_split[9]
    local_date = data_split[-11]
    url_change = 'https://finance.sina.com.cn/futures/quotes/{}.shtml'.format(code)
    browser.get(url_change)
    time.sleep(1)
    rate_data = browser.find_element_by_xpath('//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/div/p/span[2]').text
    value_data = browser.find_element_by_xpath('//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/div/p/span[1]').text
    date = browser.find_element_by_xpath('//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/p').text
    if '+' in value_data:
        change = 1
    else:
        change = 0
    #url_change_page = requests.get(url_change, headers = headers).content
    #soup = BeautifulSoup(url_change_page, 'html.parser')
    #change = soup.find('p', attrs = {'class':'change-wrap'})
    #rate_data = change.find('span', attrs = {'class':'amt'}).get_text()
    #value_data = change.find('span', attrs = {'class':'amt-value'}).get_text()
    #print(rate_data,value_data)
    data_row = [name, code, real, yesterday, open_price, high, low, close, change, rate_data[1:], value_data[1:], date, local_date] 
    #'名称','实际价','昨结算','开盘价','最高价','最低价','收盘价','变化','变化率','变化值','日期'
    return data_row

def future_data_out(code, name): #当天国外
    url = 'http://hq.sinajs.cn/?_=/&list=hf_'+code
    url_page = requests.get(url, headers = headers).text
    #print(url_page)
    pattern_str = re.compile('"(.*)"') #获取双引号内的内容
    str_data = pattern_str.findall(url_page)[0]
    data_split = str_data.split(',')
    real = data_split[0]
    open_price = data_split[8]
    high = data_split[4]
    low = data_split[5]
    yesterday = data_split[7]
    close = real
    #deal_num = data_split[14]
    url_change = 'https://finance.sina.com.cn/futures/quotes/{}.shtml'.format(code)
    browser.get(url_change)
    time.sleep(1)
    rate_data = browser.find_element_by_xpath('//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/div/p/span[2]').text
    value_data = browser.find_element_by_xpath('//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/div/p/span[1]').text
    date = browser.find_element_by_xpath('//*[@id="table-box-futures-hq"]/tbody/tr[1]/td[1]/p').text
    if '+' in value_data:
        change = 1
    else:
        change = 0
    local_date = data_split[-2]
    data_row = [name, code, real, yesterday, open_price, high, low, close, change, rate_data[1:], value_data[1:], date, local_date]
    return data_row

def up_sql_day_k(data): #数据库
    name, code, real, yesterday, open_price, high, low, close, change, rate_data, value_data, date, local_date = data
    connection = pymysql.connect(host = '47.92.25.70',user = 'root',password = 'Wfn031641',db = 'cxd_data',charset = 'utf8')
    connection_f = pymysql.connect(host = '39.105.9.20',user = 'root',password = 'bigdata_oil',db = 'cxd_data',charset = 'utf8')
    try :
        with connection.cursor() as cursor:
            sql_i = "insert into `yjt_futures_day`(`name`,`code`,`real`,`yes_settlement`,`open`,`high`,`low`,`close`,`diff_flag`,`diffPer`,            `diff`,`update_time`,`local_date`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_i,data)
        connection.commit() 
    except pymysql.err.IntegrityError:
        print('更新实时值')
        now = datetime.datetime.now()
        curr_time = now.strftime('%Y-%m-%d %H:%M:%S')
        update_row = [real, high, low, close, change, rate_data, value_data, date, curr_time, name, local_date]
        with connection.cursor() as cursor:
            sql_i = "update `yjt_futures_day` SET `real`=%s,`high`=%s,`low`=%s,`close`=%s,`diff_flag`=%s,`diffPer`=%s,            `diff`=%s, `update_time`=%s, `modify_time`=%s WHERE `name`=%s AND `local_date`=%s"
            cursor.execute(sql_i,update_row)
        connection.commit() 
        print('更新完成测试库')
    finally:
        connection.close()
        #connection_f.close()
        print('Test single is done: %s' %data[0])
        
    try:
        with connection_f.cursor() as cursor:
            sql_i = "insert into `yjt_futures_day`(`name`,`code`,`real`,`yes_settlement`,`open`,`high`,`low`,`close`,`diff_flag`,`diffPer`,            `diff`,`update_time`,`local_date`)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_i,data)
        connection_f.commit()
        #print('成功')
    except pymysql.err.IntegrityError:
        print('更新实时值')
        now = datetime.datetime.now()
        curr_time = now.strftime('%Y-%m-%d %H:%M:%S')
        update_row = [real, high, low, close, change, rate_data, value_data, date, curr_time, name, local_date]
        with connection_f.cursor() as cursor:
            sql_i = "update `yjt_futures_day` SET `real`=%s,`high`=%s,`low`=%s,`close`=%s,`diff_flag`=%s,`diffPer`=%s,            `diff`=%s, `update_time`=%s, `modify_time`=%s WHERE `name`=%s AND `local_date`=%s"
            cursor.execute(sql_i,update_row)
        connection_f.commit() 
        print('更新完成正式库')
    except Exception as e:
        print(e)
    finally:
        #connection.close()
        connection_f.close()
        print('Formal single is done: %s' %data[0])
        

#分时
def minute_in(code,name): #国内分时线
    yesd = float(futures_data(code,name)[3]) #引入前一天结算价格，计算用
    url = 'https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20t1nf_{}=/InnerFuturesNewService.getMinLine?symbol={}'.format(code,code)
    url_page = requests.get(url, headers = headers).text
    #print(url_page)
    pattern_str = re.compile('\((.*)\)') #获取括号内的内容
    str_data = pattern_str.findall(url_page)[0]
    #print(str_data)
    data = eval(str_data)
    data_row = []
    now = datetime.datetime.now()
    curr_time = now.strftime('%Y-%m-%d')
    for row in data:
        price = row[1]
        index = data.index(row)
        price_avg = row[2]
        value_c = round(float(price) - yesd,2)
        rate_c = str(round(value_c/yesd*100,2))+'%'
        d_time = row[0]
        row_single = [name, code, index, price, price_avg, value_c, rate_c, d_time, curr_time]
        data_row.append(row_single)
    return data_row
    
def minute_out(code,name): #国外分时线
    yesd = float(foreign_data(code,name)[3])
    url = 'http://stock2.finance.sina.com.cn/futures/api/json.php/GlobalFuturesService.getGlobalFuturesMinLine?symbol={}'.format(code)
    url_page = requests.get(url, headers = headers).text
    #print(url_page)
    pattern_str = re.compile(r'[{](.*)[}]') #获取大括号内的内容
    str_data = pattern_str.findall(url_page)[0]
    #print(str_data)
    data_origin = str_data[14:-1]
    #data = json.loads(data_origin)
    #print(data_origin)
    null = 'null' #原网页个别神经键名变量要定义下
    data = eval(data_origin)
    data_row = []
    list_avg = []
    now = datetime.datetime.now()
    curr_time = now.strftime('%Y-%m-%d')
    for row in data:
        price = row[-2]
        index = data.index(row)
        list_avg.append(float(price))
        f = lambda l:sum(l)/len(l)
        price_avg = round(f(list_avg),3)
        value_c = round(float(price) - yesd,3)
        rate_c = str(round(value_c/yesd*100,2))+'%'
        d_time = row[-3]
        if code == 'OIL' and d_time[:2] == '08':
            print('时间错误')
            continue
        row_single = [name, code, index, price, price_avg, value_c, rate_c, d_time, curr_time]
        data_row.append(row_single)
    return data_row

def up_sql_minute(data): #分时数据至数据库
    connection = pymysql.connect(host = '47.92.25.70',user = 'root',password = 'Wfn031641',db = 'cxd_data',charset = 'utf8')
    connection_f = pymysql.connect(host = '39.105.9.20',user = 'root',password = 'bigdata_oil',db = 'cxd_data',charset = 'utf8')
    try :
        with connection.cursor() as cursor:
            sql_i = "insert into `yjt_futures_min`(`name`,`code`,`index`,`price`,`avg_price`,`diff`,`diffPer`,`time`,`date`)                values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_i,data)
        connection.commit() 
        #print('成功')
    except pymysql.err.IntegrityError:
        pass
        #return None
    except Exception as e:
        print(e)
    finally:
        connection.close()
        #print('Single Done: %s' %data[0])
        
    try :
        with connection_f.cursor() as cursor:
            sql_i = "insert into `yjt_futures_min`(`name`,`code`,`index`,`price`,`avg_price`,`diff`,`diffPer`,`time`,`date`)                values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_i,data)
        connection_f.commit() 
        #print('成功')
    except pymysql.err.IntegrityError:
        pass
        #return None
    except Exception as e:
        print(e)
    finally:
        connection_f.close()
        
def up_single_thread():
    data_in = minute_in('SC1903', '原油1903')
    data_out_cl = minute_out('CL', 'WTI')
    data_out_oil = minute_out('OIL', '布伦特原油')
    #print(data)
    for data_i in data_in:
        up_sql_minute(data_i)
    for data_i in data_out_cl:
        up_sql_minute(data_i)
    for data_i in data_out_oil:
        up_sql_minute(data_i)
    print('Done!')
    

#分时多线程
def threading_sql(data):
    with concurrent.futures.ThreadPoolExecutor(14) as executor: 
        data_list = data
        for row, result in zip(data_list, executor.map(up_sql_minute, data_list)):
            print('目前：',row[-1])
    print(data[0][0],'is Done!')
    


if __name__ == "__main__":
    #日K
    data = futures_data('SC1907', '原油1907')
    data_cl = future_data_out('CL', 'WTI')
    data_oil = future_data_out('OIL', '布伦特原油')
    #print(data_oil)
    up_sql_day_k(data)
    up_sql_day_k(data_cl)
    up_sql_day_k(data_oil)
    
    #分时
    #up_single_thread()    
    #分时多线程
    data_in = minute_in('SC1907', '原油1907')
    data_out_cl = minute_out('CL', 'WTI')
    data_out_oil = minute_out('OIL', '布伦特原油')
    #print(data_in)
    threading_sql(data_in)
    threading_sql(data_out_cl)
    threading_sql(data_out_oil)
