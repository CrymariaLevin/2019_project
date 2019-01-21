
from selenium import webdriver
import time

from datetime import datetime
import os

import xlrd
import xlwt
import glob
from numpy import *
import sys
import os

CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.binary_location = "F:/Portable/ChromePortable/App/Google Chrome/chrome.exe"
# CHROME_OPTIONS.add_argument('headless')

# PHANTOMJS_CAP = webdriver.DesiredCapabilities.PHANTOMJS
# PHANTOMJS_CAP["phantomjs.page.settings.resourceTimeout"] = 1000
# # PHANTOMJS_CAP["phantomjs.page.settings.loadImages"] = False
# PHANTOMJS_CAP["phantomjs.page.settings.localToRemoteUrlAccessEnabled"] = True

#爬虫主程序，需传入日期和链接
def crawl_data(url,dtbgn,dtend):
    browser = webdriver.Chrome(chrome_options=CHROME_OPTIONS)
    # browser = webdriver.PhantomJS(desired_capabilities=PHANTOMJS_CAP)
    browser.get(url)#链接
    browser.find_element_by_xpath('//*[@id="LogInPart1_SciName"]').send_keys('jusure2016')
    browser.find_element_by_xpath('//*[@id="LogInPart1_SciPwd"]').send_keys('jusure2017')
    browser.find_element_by_xpath('//*[@id="LogInPart1_IB_Login"]').click()
    browser.maximize_window() 
    time.sleep(2)

    #table = browser.find_element_by_id('divContents')
    table = browser.find_elements_by_tag_name('tr')
    #print(table)

    oil_id = []
    for tr_id in table:
        img_id = tr_id.get_attribute("id")
        if img_id:
            oil_id.append(img_id)
        else:
            pass

    time.sleep(1)
    #browser.maximize_window()
    # actionChains = ActionChains(browser)

    small_list = [oil_id[i:i+10] for i in range(0,len(oil_id),10)]#每10个一选
    for i, id_list in enumerate(small_list):
        print("group {0}, id list = {1}".format(i+1, id_list))
        for j, id in enumerate(id_list):
            # print("click #img{}".format(id))
            # if i == 0:
            #     # actionChains.move_to_element(browser.find_element_by_xpath('//*[@id="img{}"]'.format(id))).perform()
            #     # browser.execute_script("document.getElementById('{0}').scrollTop=10000".format("img{0}".format(id)))
            #     # elem_img = browser.find_element_by_xpath('//*[@id="img{}"]'.format(id))
            #     # browser.execute_script("arguments[0].scrollIntoView();", elem_img)
            #     browser.execute_script("arguments[0].click();", elem_img)
            #     time.sleep(0.5)
            # browser.find_element_by_xpath('//*[@id="img{}"]'.format(id)).click()#选择需下载的信息
            # elem_img.click()#选择需下载的信息
            elem_img = browser.find_element_by_xpath('//*[@id="img{}"]'.format(id))
            browser.execute_script("arguments[0].click();", elem_img)
            time.sleep(0.5)

        time.sleep(2)

        browser.find_element_by_xpath('//*[@id="basket_close"]/a').click()
        time.sleep(2)
        browser.find_element_by_xpath('//*[@id="txtLineStartDate"]').clear()
        browser.find_element_by_xpath('//*[@id="txtLineStartDate"]').send_keys(dtbgn)#当天日期
        browser.find_element_by_xpath('//*[@id="txtLineEndDate"]').clear()
        browser.find_element_by_xpath('//*[@id="txtLineEndDate"]').send_keys(dtend)#当天日期
        browser.find_element_by_xpath('//*[@id="boxhistorylink"]/b').click()
        browser.switch_to_window(browser.window_handles[-1])
        time.sleep(2)
        browser.find_element_by_xpath('//*[@id="lbTOExcel_original"]').click()
        time.sleep(1)
        browser.close()#关闭新窗口，节省内存

        browser.switch_to_window(browser.window_handles[0])#返回首页重新选取
        browser.find_element_by_xpath('//*[@id="basket_close"]/div/div[1]/div[3]/a[2]/b').click()#清空数据
        browser.find_element_by_xpath('//*[@id="basket_close"]/a').click()#将点开的界面点掉


#根据日期和油品名保存文件
def merge_data(name, dtbgn, dtend):
    #date = today
    biaotou=['时间','产品名称','最低价','最高价','平均价','单位','型号','生产企业','市场','区域','省','市','价格条件','备注','发改委零售限价','发改委批发限价']  

    filelocation="C:/Users/xinxi/Downloads/"  #搜索多个表格存放处
    fileform="xls"  #当前文件夹下搜索的文件名后缀  

    # filedestination="C:/Users/xinxi/Downloads/"+name+"/"  #将合并后的表格存放到的位置
    filedestination="./{0}/"  #将合并后的表格存放到的位置
    if dtbgn != dtend:
        file="卓创_价格_{}_{}_{}".format(name,dtbgn,dtend) #合并后的表格名
    else:
        file="卓创_价格_{}_{}".format(name,dtbgn) #合并后的表格名

    if not os.path.exists(filedestination):
        os.makedirs(filedestination)

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
    sheet=filename.add_sheet(dtbgn)  #新表格的sheet名（date）

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
    filename.save(filedestination+file+".xls")  

#油品品类及链接存放处
dict_url = {
    # 2018-05-31
    '主营柴油': 'http://price.sci99.com/view/PriceView.aspx?pagename=energyView&classid=922&linkname=%e4%b8%bb%e8%90%a5%e6%9f%b4%e6%b2%b9&pricetypeid=24',

    # 2018-05-31
    '主营汽油': 'http://price.sci99.com/view/PriceView.aspx?pagename=energyView&classid=921&linkname=%e6%88%90%e5%93%81%e6%b2%b9',

    # 2018-06-01
    # '主营柴油': 'http://price.sci99.com/view/PriceView.aspx?pagename=energyView&classid=922&linkname=%e4%b8%bb%e8%90%a5%e6%9f%b4%e6%b2%b9&pricetypeid=24',

    # 2017-01-01
    # '地炼柴油': 'http://price.sci99.com/view/PriceView.aspx?pagename=energyView&classid=922&pricetypeid=41&linkname=%e5%9c%b0%e7%82%bc%e6%9f%b4%e6%b2%b9',

    # 2017-01-01
    # '地炼汽油': 'http://price.sci99.com/view/PriceView.aspx?pagename=energyView&classid=921&pricetypeid=41&linkname=%e5%9c%b0%e7%82%bc%e6%b1%bd%e6%b2%b9',

    # '燃料油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=273&linkname=%E7%87%83%E6%96%99%E6%B2%B9&RequestId=8666a32cb031681b',
    # '成品油': 'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&linkname=%E6%88%90%E5%93%81%E6%B2%B9&RequestId=5e4b79a113456ddb'
}

filelocation="C:/Users/xinxi/Downloads/"#下载表格位置

def main():
    
    now = datetime.now()
    # today = "2018-06-01" #获取当日日期
    # today = "2018-05-31" #获取当日日期
    # endday = "2018-05-31"
    # today = now.strftime('%Y-%m-%d')#获取当日日期
    dtbgn = "2018-05-31"
    # dtend = now.strftime("%Y-%m-%d")
    dtend = "2018-05-31"

    for oil_name in dict_url:
        name = oil_name
        url = dict_url[name]
        # crawler(today,url)
        crawl_data(url, dtbgn, dtend)
        # price_today(today,name)
        merge_data(name, dtbgn, dtend)
        for file_name in glob.glob(filelocation+"*."+'xls'):#遍历文件夹内xls文件，删除后为下个品类做准备
            os.remove(file_name)
    
if __name__ == "__main__":
    main()


# In[ ]:


#单独调试处
# def main():
#     today = '2018-06-01'
#     name = '燃料油'
#     #name = '成品油'
#     #燃料油
#     url = 'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=273&linkname=%E7%87%83%E6%96%99%E6%B2%B9&RequestId=8666a32cb031681b'
#     #c成品油
#     #url = 'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&linkname=%E6%88%90%E5%93%81%E6%B2%B9&RequestId=5e4b79a113456ddb'
#     crawler(today,url)
#     price_today(today,name)
#
# if __name__ == "__main__":
#     main()

