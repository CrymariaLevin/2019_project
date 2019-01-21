
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from config_oil import *
from datetime import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#import logging

filelocation=file_route['origin_download_loc']#下载表格位置
now = datetime.now()
today = now.strftime('%Y-%m-%d')#获取当日日期

#logger = logging.getLogger()
#logger.setLevel(logging.INFO)  # Log等级总开关

def clear_xls():
    for file_name in glob.glob(filelocation+"*."+'xls'):#遍历文件夹内xls文件，删除后为下个品类做准备
            os.remove(file_name)

#爬虫主程序，需传入日期和链接
def crawler(date,url,date_e = today):
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10) #等待的最大时间
    browser.get(url)#链接
    browser.find_element_by_xpath('//*[@id="LogInPart1_SciName"]').send_keys('jusure2016')
    browser.find_element_by_xpath('//*[@id="LogInPart1_SciPwd"]').send_keys('jusure2017')
    browser.find_element_by_xpath('//*[@id="LogInPart1_IB_Login"]').click()
    #browser.maximize_window() 

    #wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="classname"]')))#判断该元素是否出现
        
    if url == oil_url_market['主营柴油']:
        time.sleep(14) 
    else:
        time.sleep(7)
    
    #table = browser.find_element_by_id('divContents')
    table = browser.find_elements_by_tag_name('tr')
    #print(table)

    oil_id = []
    for tr_id in table:
        img_id = tr_id.get_attribute("id") #获取按钮的id值
        if img_id:
            oil_id.append(img_id)
        else:
            pass
    
    time.sleep(1)
    #browser.maximize_window() 

    small_list = [oil_id[i:i+10] for i in range(0,len(oil_id),10)]#每10个一选
    table_num = len(small_list)
    for id_list in small_list:
        for id in id_list:
            elem_img = browser.find_element_by_xpath('//*[@id="img{}"]'.format(id))
            browser.execute_script("arguments[0].click();", elem_img)
            time.sleep(0.5)

        try:
            browser.find_element_by_xpath('//*[@id="basket_close"]/a').click()
            time.sleep(2)
            browser.find_element_by_xpath('//*[@id="txtLineStartDate"]').clear()
            browser.find_element_by_xpath('//*[@id="txtLineStartDate"]').send_keys(date)#当天日期
            browser.find_element_by_xpath('//*[@id="txtLineStartDate"]').send_keys(Keys.TAB) #注意必须要加tab，否则报错
            browser.find_element_by_xpath('//*[@id="txtLineEndDate"]').send_keys(date_e)#结束日期
            time.sleep(1)
            browser.find_element_by_xpath('//*[@id="boxhistorylink"]/b').click()
            browser.switch_to_window(browser.window_handles[-1])
            time.sleep(1)
            submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="lbTOExcel_original"]')))#判断该元素是否可以点击
            #download.click()
            submit.click()
            #browser.find_element_by_xpath('//*[@id="lbTOExcel_original"]').click()
            time.sleep(1)
            browser.close()#关闭新窗口，节省内存
        except:
            print('页面出现问题，重新爬取')
            clear_xls()
            crawler(date,url,date_e = today)

        browser.switch_to_window(browser.window_handles[0])#返回首页重新选取
        browser.find_element_by_xpath('//*[@id="basket_close"]/div/div[1]/div[3]/a[2]/b').click()#清空数据
        browser.find_element_by_xpath('//*[@id="basket_close"]/a').click()#将点开的界面点掉
        time.sleep(1)
    print('网页爬取完成')
    return table_num

import xlrd
import xlwt
import glob  
from numpy import * 

#根据日期和油品名保存文件
def price_today(date,name,date_e = today):
    #date = today
    biaotou=['时间','产品名称','最低价','最高价','平均价','单位','型号','生产企业','市场','区域','省','市','价格条件','备注','发改委零售限价','发改委批发限价']  

    filelocation = file_route['origin_download_loc']  #搜索多个表格存放处 
    fileform="xls"  #当前文件夹下搜索的文件名后缀  

    filedestination = file_route['oil_market_loc']+name+"//"  #将合并后的表格存放到的位置  
    file="卓创_市场价格_{}_{}_{}".format(name,date,date_e) #合并后的表格名 

    #首先查找默认文件夹下有多少文档需要整合  
     
    filearray=[]  
    for filename in glob.glob(filelocation+"*."+fileform):  
        filearray.append(filename)  
    #以上是从pythonscripts文件夹下读取所有excel表格，并将所有的名字存储到列表filearray 

    print("在默认文件夹下有%d个文档"%len(filearray))  
    ge=len(filearray)  
    matrix = [None]*ge  
    #实现读写数据  

    #下面是将所有文件读数据到三维列表cell[][][]中（不包含表头）  
    #import xlrd  
    for i in range(ge):  
        fname=filearray[i]  
        bk=xlrd.open_workbook(fname)  
        try:  
            sh=bk.sheet_by_name("产品的原始历史数据")  #下载的sheet名字
        except:  
            print ("在文件%s中没有找到sheet1，读取文件数据失败,注意表格sheet的名字" %fname)  
        nrows=sh.nrows   
        matrix[i] = [0]*(nrows-1)  

        ncols=sh.ncols  
        for m in range(nrows-1):    
            matrix[i][m] = ["0"]*ncols  

        for j in range(1,nrows):  
            for k in range(0,ncols):  
                matrix[i][j-1][k]=sh.cell(j,k).value  

    #下面是写数据到新的合并表格中  
    #import xlwt  
    filename=xlwt.Workbook()  
    sheet=filename.add_sheet(date)  #新表格的sheet名（date）

    #下面是把表头写上  
    for i in range(0,len(biaotou)):  
        sheet.write(0,i,biaotou[i])  

    #求和前面的文件一共写了多少行  
    zh=1  
    for i in range(ge):  
        for j in range(len(matrix[i])):  
            for k in range(len(matrix[i][j])):  
                sheet.write(zh,k,matrix[i][j][k])  
            zh=zh+1 
    print("我已经将%d个文件合并成1个文件，并命名为%s.xls."%(ge,file))
    #rq = time.strftime('%Y%m%d', time.localtime(time.time()))
    #log_path = 'D:/Logs/'
    #log_name = rq + '.log'
    #logfile = log_path + log_name
    #fh = logging.FileHandler(logfile, mode='a')
    #fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
    #formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    #fh.setFormatter(formatter)
    #logger.addHandler(fh)
    #logger.info("我已经将%d个文件合并成1个文件，并命名为%s.xls."%(ge,file))
    filename.save(filedestination+file+".xls") 
    #return ge

def form_num():
    filelocation = file_route['origin_download_loc']  #搜索多个表格存放处 
    fileform="xls"  #当前文件夹下搜索的文件名后缀  
   
    #首先查找默认文件夹下有多少文档需要整合  
    filearray=[]  
    for filename in glob.glob(filelocation+"*."+fileform):  
        filearray.append(filename)  
    ge=len(filearray) 
    return ge

from datetime import datetime
import os
import re
from config_oil import *

now = datetime.now()
today = now.strftime('%Y-%m-%d')#获取当日日期
#browser = webdriver.Chrome()

def main():
    #today = '2018-06-09'
    date_stamp = now.timestamp()- 1327121 #14天前
    date = datetime.fromtimestamp(date_stamp).strftime('%Y-%m-%d')
    
    for oil_name in oil_url_market:
        name = oil_name
        url = oil_url_market[name]        
        #crawler(date,url)
        web_n,local_n = crawler(date,url),form_num()
        print('web_n is {},local_n is {}'.format(web_n, local_n))
        
        '''while web_n != local_n: #如果下载数量与爬取实际数量不符，重新爬取。
            print('条目不符，重新爬取')
            #browser.close()
            clear_xls()
            #crawler(date,url)
            web_n,local_n = crawler(date,url),form_num()
            print('web_n is {},local_n is {}'.format(web_n, local_n))
            price_today(date,name)
            '''
        price_today(date,name)
        clear_xls()
        time.sleep(2)        
    
if __name__ == "__main__":
    main()
#2,44/42/35,15,13


