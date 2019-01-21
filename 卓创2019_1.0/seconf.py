from selenium import webdriver        
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui

CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.binary_location = "D:/ChromePortable/App/Google Chrome/chrome.exe"
CHROME_PREFS = {"profile.managed_default_content_settings.images":2}
# CHROME_OPTIONS.add_experimental_option("prefs",CHROME_PREFS)
CHROME_DRVPATH = "D:/ChromeDriver-2.37/chromedriver.exe"

PHANTOMJS_CAP = webdriver.DesiredCapabilities.PHANTOMJS
PHANTOMJS_CAP["phantomjs.page.settings.resourceTimeout"] = 1000
# PHANTOMJS_CAP["phantomjs.page.settings.loadImages"] = False
PHANTOMJS_CAP["phantomjs.page.settings.localToRemoteUrlAccessEnabled"] = True

class SpiderProxy(object):
    # CHROME_OPTIONS = webdriver.ChromeOptions()
    # CHROME_OPTIONS.binary_location = "D:/ChromePortable/App/Google Chrome/chrome.exe"
    # # CHROME_PREFS = {"profile.managed_default_content_settings.images":2}
    # # CHROME_OPTIONS.add_experimental_option("prefs",CHROME_PREFS)
    # CHROME_DRVPATH = "D:/ChromeDriver-2.37/chromedriver.exe"
    #
    # PHANTOMJS_CAP = webdriver.DesiredCapabilities.PHANTOMJS
    # PHANTOMJS_CAP["phantomjs.page.settings.resourceTimeout"] = 1000
    # PHANTOMJS_CAP["phantomjs.page.settings.loadImages"] = False
    # PHANTOMJS_CAP["phantomjs.page.settings.localToRemoteUrlAccessEnabled"] = True

    def __init__(self, drv_type="phantomjs", load_img=False):
        if not load_img:
            CHROME_OPTIONS.add_experimental_option("prefs", CHROME_PREFS)
            PHANTOMJS_CAP["phantomjs.page.settings.loadImages"] = False
        if drv_type == "phantomjs":
            self.webdrv = webdriver.PhantomJS(desired_capabilities=PHANTOMJS_CAP)
        else:
            self.webdrv = webdriver.Chrome(CHROME_DRVPATH, chrome_options=CHROME_OPTIONS) # 打开谷歌浏览器
        self.drvwait = ui.WebDriverWait(self.webdrv, 10)