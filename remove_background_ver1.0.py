
# coding: utf-8

# In[7]:


#!/usr/bin/python
# -*- coding: utf-8 -*-
#Author: Selvaria
#https://www.remove.bg/profile#api-key

from removebg import RemoveBg
import os

key = 'cK5JQaCRHid3LFaK5RrKCrCR'

rb = RemoveBg(key, './error_log_rb/error.log')

path = r'D:\picture\去背景测试\07311'

for pic in os.listdir(path):
    rb.remove_background_from_img_file(path+'/%s' %pic, size='regular') #regular, hd, 4k 根据要处理的图片大小选择
    print('完成%s' %pic)


# In[8]:


a = True
~a

