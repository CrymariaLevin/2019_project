
# !/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Selvaria
# 石化相关新闻爬取
# 中石油新闻中心 http://news.cnpc.com.cn/hynews/
# 中石化新闻网 http://www.sinopecnews.com.cn/news/node_11043.html

import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pymysql
from DBUtils.PooledDB import PooledDB


class MysqlPool(object): #设置数据库连接池和初始化    
    """
        MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
        获取连接对象：conn = Mysql.get_connection()
        释放连接对象;conn.close()或del conn
    """
    
    def __init__(self,mincached=5, maxcached=14,
                maxconnections=244, blocking=True, maxshared=0):
        """
            生成MySQL数据库连接池
        :param mincached: 最少的空闲连接数，如果空闲连接数小于这个数，pool会创建一个新的连接
        :param maxcached: 最大的空闲连接数，如果空闲连接数大于这个数，pool会关闭空闲连接
        :param maxconnections: 最大的连接数
        :param blocking: 当连接数达到最大的连接数时，在请求连接的时候，如果这个值是True，请求连接的程序会一直等待，
                          直到当前连接数小于最大连接数，如果这个值是False，会报错，
        :param maxshared: 当连接数达到这个数，新请求的连接会分享已经分配出去的连接
        """        
        db_config = {
            "host": '47.92.25.70',
            "port": 3306,
            "user": 'root',
            "passwd": 'Wfn031641',
            "db": 'cxd_data',
            "charset": 'utf8'
        }
        self.pool = PooledDB(pymysql, mincached=mincached, maxcached=maxcached, maxconnections=maxconnections,
                             blocking=blocking, maxshared=maxshared, **db_config)

    def get_connection(self):
        return self.pool.connection()

    def close(self):
        self.pool.close()

    def __del__(self):
        self.close()

# 获取mysql数据库服务器的连接
def get_dbservice_mysql_conn(): #实例化连接池类，方便调用
    """
    :return: Object  MySQL Connection
    """
    global _dbservice_pool
    if not _dbservice_pool or not isinstance(_dbservice_pool, MysqlPool):
        _dbservice_pool = MysqlPool()
    return _dbservice_pool.get_connection()

_dbservice_pool = None



class News(object):
    
    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        }
    
    def __init__(self):
        pass
    
    
class CNPCNews(News): # 中石油新闻中心    
    
    url = 'http://news.cnpc.com.cn/hynews/'
    
    def __init__(self):
        pass
    
    def get_news_data(self):
        url_byte = requests.get(self.url, headers = self.headers)#.content
        url_byte.encoding = 'gb18030'  #政府网站编码不统一，无语
        soup = BeautifulSoup(url_byte.text, 'html.parser') #注意转为str格式
        CHROME_OPTIONS = webdriver.ChromeOptions()
        CHROME_OPTIONS.add_argument('headless')
        browser = webdriver.Chrome(chrome_options=CHROME_OPTIONS)
        list_title = soup.find('div', attrs = {'class':'list18'})
        news_soup = list_title.find_all('li', attrs={'class':'ejli'})
        news_list = []
        for soup in news_soup:
            title = soup.find('a', attrs={'target':'_blank'}).get_text()
            link = soup.find('a')['href']
            browser.get(link)
            time.sleep(1)
            content = browser.find_element_by_xpath('//*[@id="newsmain-ej"]/div/div[1]/div[1]/div[4]/div').text
            date = soup.find('span', attrs={'class':'fr as07'}).get_text()
            news_single = [title, content, link, date]
            news_list.append(news_single)
        return news_list
    
    def up_sql_cnpc(self):
        data = self.get_news_data()
        [data_i.append(1) for data_i in data]
        #print(data)
        connection = get_dbservice_mysql_conn()
        connection_f = pymysql.connect(host = '39.105.9.20',user = 'root',password = 'bigdata_oil',db = 'cxd_data',charset = 'utf8')
        for news_data in data:
            try:
                with connection.cursor() as cursor:
                    sql = "insert into `oil_news_detail` (`title`,`content`,`link`,`date`,`source`) values(%s,%s,%s,%s,%s)"
                    cursor.execute(sql,news_data)
                connection.commit()
            except pymysql.err.IntegrityError:
                continue
            except Exception as e:
                print('测试库写入失败')
                print(str(e))
            try:
                with connection_f.cursor() as cursor:
                    sql = "insert into `oil_news_detail` (`title`,`content`,`link`,`date`,`source`) values(%s,%s,%s,%s,%s)"
                    cursor.execute(sql,news_data)
                connection_f.commit()
            except pymysql.err.IntegrityError:
                continue
            except Exception as e:
                print('正式库写入失败')
                print(str(e))
        print('本日中石油新闻数据写入完成')
        

class SNPCNews(News): # 中石化新闻网
    
    url = 'http://www.sinopecnews.com.cn/news/node_11043.html'
    
    def __init__(self):
        pass
    
    def get_news_data(self):
        browser = webdriver.Chrome()
        browser.get(self.url)
        time.sleep(1)
        browser.switch_to.frame('main')
        elem_img = browser.find_element_by_xpath('/html/body/table[9]/tbody/tr/td[2]/table[1]/tbody/tr/td/a')
        browser.execute_script("arguments[0].click();", elem_img)
        browser.switch_to_window(browser.window_handles[-1])
        time.sleep(1)
        table = browser.find_element_by_xpath('/html/body/table[5]/tbody/tr/td[2]/table[3]/tbody/tr/td/table')
        title_list = table.find_elements_by_tag_name('tr')
        news_list = []
        for row in title_list:
            try:
                title = row.find_elements_by_tag_name('td')[0].text
                title = title.replace('·','')
                link = row.find_element_by_tag_name('a').get_attribute("href")
                date = row.find_elements_by_tag_name('td')[-1].text
                browser.switch_to_window(browser.window_handles[0])
                browser.get(link)
                time.sleep(1)
                content = browser.find_element_by_xpath('//*[@id="content"]/table[6]/tbody/tr/td').text
                news_single = [title, content, link, date]
                news_list.append(news_single)
                browser.switch_to_window(browser.window_handles[1])
                time.sleep(0.5)
            except:
                continue
        return news_list
    
    def up_sql_snpc(self):
        data = self.get_news_data()
        [data_i.append(2) for data_i in data]
        #print(data)
        connection = get_dbservice_mysql_conn()
        connection_f = pymysql.connect(host = '39.105.9.20',user = 'root',password = 'bigdata_oil',db = 'cxd_data',charset = 'utf8')
        for news_data in data:
            try:
                with connection.cursor() as cursor:
                    sql = "insert into `oil_news_detail` (`title`,`content`,`link`,`date`,`source`) values(%s,%s,%s,%s,%s)"
                    cursor.execute(sql,news_data)
                connection.commit()
            except pymysql.err.IntegrityError:
                continue
            except Exception as e:
                print('测试库写入失败')
                print(str(e))
                
            try:
                with connection_f.cursor() as cursor:
                    sql = "insert into `oil_news_detail` (`title`,`content`,`link`,`date`,`source`) values(%s,%s,%s,%s,%s)"
                    cursor.execute(sql,news_data)
                connection_f.commit()
            except pymysql.err.IntegrityError:
                continue
            except Exception as e:
                print('正式库写入失败')
                print(str(e))
        print('本日中石化新闻数据写入完成')
        
        
def main():
    c = CNPCNews()
    c.up_sql_cnpc()
    s = SNPCNews()
    s.up_sql_snpc()
        

if __name__ == "__main__":        
    main()
