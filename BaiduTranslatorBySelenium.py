import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait as WD


class BaiduSelenium:

    def __init__(self, opt=None, chrome_path=r"F:\Downloads\chromedriver.exe", outTime=5):
        self.lastRes = None
        self.outTime = outTime
        self.count = 0

        if isinstance(opt, list):
            if len(opt) != 0:
                for t in opt:
                    if not isinstance(opt[0], tuple) or not len(opt[0]) == 2:
                        print(opt[0], "must be tuple and be (function,args)")
                        exit(-1)
            else:
                pass
        else:
            if opt is None:
                pass
            else:
                print("opt must be list")
                exit(-1)

        options = Options()  # 模拟器设置
        options.add_argument('--headless')  # 浏览器不提供可视化页面
        options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
        options.add_argument('lang=zh_CN.UTF-8')
        # 添加UA
        options.add_argument(
            'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"')
        # 指定浏览器分辨率
        # options.add_argument('window-size=1920x3000')
        # 添加crx插件
        # options.add_extension('d:\crx\AdBlock_v2.17.crx')
        # 设置开发者模式启动，该模式下webdriver属性为正常值   一般反爬比较好的网址都会根据这个反爬
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chromeService = Service(executable_path=chrome_path)
        self.driver = webdriver.Chrome(service=chromeService, options=options)
        self.driver.maximize_window()
        self.reset()

    def reset(self):
        self.driver.get("https://fanyi.baidu.com")
        # while True:
        #     pass
        time.sleep(2)
        self.clearAlert()
        self.lastRes = ""
        self.count = 0

    def findEle(self, by, locator):
        try:
            # print('[Info:start find the elements "{}" by "{}"!]'.format(locator, by))
            elements = WD(self.driver, self.outTime).until(lambda x: x.find_element(by, locator))
        except TimeoutException as t:
            # print('error: found "{}" timeout!'.format(locator), t)
            return None
        else:
            return elements

    def clearAlert(self):
        # alerts = self.driver.find_elements(By.XPATH, '//div[@id="app-guide"]')
        # if alerts:
        #     self.driver.execute_script(
        #         """
        #     var element = document.querySelector('//div[@id="app-guide"]');
        #     if (element)
        #         element.parentNode.removeChild(element);
        #     """
        #     )
        alerts = self.findEle(By.XPATH, '//span[@class="app-guide-close"]')
        if alerts:
            alerts.click()

    def getRes(self, count=0):
        count = count + 1
        if count >= 60:
            print("getRes err")
            return ""
        res = self.findEle(By.XPATH, "//p[@class='ordinary-output target-output clearfix']")
        if res is not None:
            if self.lastRes != res.text:
                self.lastRes = res.text
                return res.text
        time.sleep(1)
        return self.getRes(count)

    def translate(self, query):
        self.count = self.count + 1
        if self.count > 20:
            self.reset()
            self.count = 0

        ele = self.driver.find_element(By.ID, "baidu_translate_input")
        ele.clear()
        ele.send_keys(query)
        self.driver.find_element(By.ID, "translate-button").click()
        return self.getRes()


if __name__ == '__main__':
    bt = BaiduSelenium()
    print(bt.translate("test"))
    print(bt.translate("this is a test"))
    print(bt.translate("test3"))
