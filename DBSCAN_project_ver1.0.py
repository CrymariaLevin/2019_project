
# coding: utf-8

# In[9]:


import pandas
import numpy as np
import math

def distance_calc(l1,l2): #计算坐标间距离，l1.l2长度需相同
    l_minus = []
    for i in range(len(l1)):
        li = l1[i]-l2[i]
        l_minus.append(li)
    sum_l = sum(x*x for x in l_minus)
    distance = math.sqrt(sum_l)
    return distance

df = pandas.read_csv('D:/all_dbscan.csv', encoding='gb18030') #原始数据
df_count = pandas.read_csv('D:/type_count.csv') #各个类型划分的编号和数量
df_digital = pandas.read_csv('D:/all_digital_dbscan.csv') #数字化后的数据（带类型）

class MostSimilarDbs(object):
    
    def __init__(self, name):
        self.name = name
        
    def get_sim10_list(self):
        df_digital = pandas.read_csv('D:/all_digital_dbscan.csv')
        com_index = df[df['com']==self.name].index.tolist()[0] #查找单位的index
        dbs_code = df['dbscan_code'][df['com']==self.name].values[0] #查找单位的分类编号
        df_middle = df_digital[df_digital['dbscan_code']==dbs_code] #取得该企业分类编号下的所有企业列表
        df_x = df_middle[['capital_num','insured','province','city','person','com_type','industry','member']]
        row = df_x.loc[com_index]
        row_core = list(row) #查找单位的坐标
        row_df = []
        for index in df_x.index:
            row_index = df_x.loc[index]
            row_calc = list(row_index)
            distance = distance_calc(row_calc,row_core)
            row_df.append([index,distance])
        df_distance = pandas.DataFrame(row_df,columns=['index','distance'])
        df_sort = df_distance.sort_values('distance',ascending= True) 
        index_list = []
        df_most10 = df_sort.head(11)
        for i in df_most10.index:
            index_m = df_most10.loc[i,'index']
            index_list.append(index_m)
        index_list.pop(0)
        return index_list
    
    def dbs_return(self):
        dbs_code = df['dbscan_code'][df['com']==self.name].values[0]
        com_index = df[df['com']==self.name].index.tolist()[0]
        df_middle = df_digital[df_digital['dbscan_code']==dbs_code]
        #print(df_middle)
        if dbs_code == -1:
            return None
        elif len(df_middle) <= 10:
            #print(df_middle)
            #com_index = df[df['com']==self.name].index.tolist()[0]
            df_middle.drop(df.index[com_index],axis=0,inplace=True)
            small_list = df_middle.index.tolist()
            return small_list
        else:
            index_list = self.get_sim10_list()
            return index_list
        
    def get_rela_name(self, list_index):
        if list_index is None:
            print('无相关企业')
            return None
        company_list = []
        for i in list_index:
            com_name = df.loc[i,'com']
            company_list.append(com_name)
        return company_list
        

def main():
    #msd = MostSimilarDbs('山东中胜石油化工有限公司')
    msd = MostSimilarDbs('威海新平液化气站')
    l = msd.dbs_return()
    print(l)
    com = msd.get_rela_name(l)
    print(com)
    
main()


# In[5]:


df.loc[42267]


# In[10]:


df[df['dbscan_code']==3484]

