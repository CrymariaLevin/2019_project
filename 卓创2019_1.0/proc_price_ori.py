
# coding: utf-8


__author__ = 'tangyj'


import proc_price_factory as ppf
import proc_price_market as ppm
import price_by_day_factory as pfd
import price_by_day_market as pmd
import proc_price_factory_test as ppf_t
import proc_price_market_test as ppm_t
import datetime as DT
import os
import shutil
import glob
from config_oil import *

def crawler():
    pfd.main()
    pmd.main()
    
def proc_price(datadir):
    ppf.init_data()
    ppf.job_datadir(datadir)
    ppm.init_data()
    ppm.job_datadir(datadir)
    ppf_t.init_data()
    ppf_t.job_datadir(datadir)
    ppm_t.init_data()
    ppm_t.job_datadir(datadir)
    
def copy_file(dir_): #建立准备进行复制的文件夹
    now = DT.datetime.now()
    today = now.strftime('%Y-%m-%d')#获取当日日期
    date_e =today
    date_stamp = now.timestamp()- 1327144 #14天前
    date = DT.datetime.fromtimestamp(date_stamp).strftime('%Y-%m-%d')

    name_f = [x for x in oil_url_factory]
    today_store = now.strftime('%Y%m%d')#本地文件夹格式
    #cur_dir = 'E:/data/zhuochuang/'

    for name in name_f:
        file="卓创_出厂价格_{}_{}_{}.xls".format(name,date,date_e)#复制后的文件名
        #print(file)
        for file_name in glob.glob(file_route['oil_factory_loc']+name+'/'+"*"+date_e+'.xls'):#遍历文件夹内当日文件
            shutil.copy(file_name,dir_ + '/' + today_store +'/{}'.format(file)) #复制前后的位置，写到文件的类型结束
            print('复制完成:%s' %file)

    name_m = [x for x in oil_url_market]
    for name in name_m:
        file="卓创_市场价格_{}_{}_{}.xls".format(name,date,date_e)
        for file_name in glob.glob(file_route['oil_market_loc']+name+'/'+"*"+date_e+'.xls'):
            shutil.copy(file_name,dir_ + '/' + today_store +'/{}'.format(file))
            print('复制完成:%s' %file)      
    

if __name__ == "__main__":
    crawler()
    cur_dir = 'E:/data/zhuochuang/'
    folder_name = DT.date.today().strftime("%Y%m%d")
    if os.path.isdir(cur_dir): #使用了os.path.isdir函数判断已有文件夹的路径是否正确。
        try:
            os.mkdir(os.path.join(cur_dir, folder_name)) 
        except:
            pass
    copy_file(cur_dir)
    DIR = cur_dir + folder_name
    proc_price(DIR)

