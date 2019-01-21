file_route = {
    'origin_download_loc' : 'C:/Users/PC/Downloads//',
    'oil_factory_loc' : 'C:/Users/PC/Downloads/出厂价/',
    'oil_market_loc' : 'C:/Users/PC/Downloads/市场价/'
    }

file_route_csv = {
    'origin_download_loc' : 'D:/Downloads//',
    'oil_factory_loc' : 'D:/Downloads/出厂价/',
    'oil_market_loc' : 'D:/Downloads/市场价/'
    }

oil_url_factory = {
    '燃料油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=273&linkname=%E7%87%83%E6%96%99%E6%B2%B9&RequestId=8666a32cb031681b',
    '主营柴油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=922&linkname=%E4%B8%BB%E8%90%A5%E6%9F%B4%E6%B2%B9&pricetypeid=24&RequestId=43593e92f7c4f258',
    '地炼柴油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=922&pricetypeid=41&linkname=%E5%9C%B0%E7%82%BC%E6%9F%B4%E6%B2%B9&RequestId=952e6c08cb198f31',
    #'主营92#汽油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&%E7%89%8C%E5%8F%B7=92%23&linkname=%E4%B8%BB%E8%90%A592%23%E6%B1%BD%E6%B2%B9&pricetypeid=24&RequestId=2c88d9eb7ca996e9',
    #'主营95#汽油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&%E7%89%8C%E5%8F%B7=95%23&linkname=%E4%B8%BB%E8%90%A595%23%E6%B1%BD%E6%B2%B9&pricetypeid=24&RequestId=7c34d8240814b11a',
    '地炼汽油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&pricetypeid=41&linkname=%E5%9C%B0%E7%82%BC%E6%B1%BD%E6%B2%B9&RequestId=f08ad7aa83ba6f81',
    '煤油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=939&linkname=%E7%85%A4%E6%B2%B9&pricetypeid=24&RequestId=2d462470e9184602'
    }
    
oil_url_market = {
    '燃料油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=273&linkname=%E7%87%83%E6%96%99%E6%B2%B9&pricetypeid=25&RequestId=2309cef3ff9218f0',
    '主营柴油': 'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=922&pricetypeid=25&linkname=%E4%B8%BB%E8%90%A5%E6%9F%B4%E6%B2%B9&RequestId=b3468c427aab550',
#    '地炼柴油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=922&linkname=%E5%9C%B0%E7%82%BC%E6%9F%B4%E6%B2%B9&pricetypeid=25&RequestId=11d74bbceaade8bf',
    '主营92#汽油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&pricetypeid=25&%E7%89%8C%E5%8F%B7=92%23&linkname=%E4%B8%BB%E8%90%A592%23%E6%B1%BD%E6%B2%B9&RequestId=17e476c6687cf226',
    '主营95#汽油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&pricetypeid=25&%E7%89%8C%E5%8F%B7=95%23&linkname=%E4%B8%BB%E8%90%A595%23%E6%B1%BD%E6%B2%B9&RequestId=ad9736c5af162377',
#    '地炼汽油':'http://price.sci99.com/view/priceview.aspx?pagename=energyview&classid=921&linkname=%E5%9C%B0%E7%82%BC%E6%B1%BD%E6%B2%B9&pricetypeid=25&RequestId=89bd8fef43f697cd'
    }

oil_check_dict = {'主营92#汽油': '地炼汽油', '主营95#汽油': '地炼汽油', '主营柴油': '地炼柴油'}

