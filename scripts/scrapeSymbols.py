from selenium import webdriver
import os
import time
from tinydb import TinyDB, Query

db=TinyDB('symbols.json')
user=Query()

driver = webdriver.Chrome(os.getcwd()+"\chromedriver.exe")
url="https://coinmarketcap.com/?page=2"
driver.get(url)
driver.execute_script("document.body.style.zoom='100%'")
driver.set_window_size(1920,1080,driver.window_handles[0])
driver.maximize_window()
time.sleep(10)

a=driver.find_element_by_xpath("//*[@id='__next']/div/div[1]/div[2]/div/div[1]/div[5]/table/tbody")
# complete XPATH: "//*[@id='__next']/div/div[1]/div[2]/div/div[1]/div[5]/table/tbody/tr[1]/td[3]/div/a/div/div/p"

for i in range(1,101):
    index=str(i)
    idpath=a.find_element_by_xpath(".//tr["+index+"]/td[3]/div/a/div/div/p")
    id=idpath.get_attribute("innerHTML")
    symbolpath=a.find_element_by_xpath(".//tr["+index+"]/td[3]/div/a/div/div/div/p")
    symbol=symbolpath.get_attribute("innerHTML")
    symbol=symbol.replace(' ','-')
    symbol=symbol.replace('.','-').lower()
    id=id.replace(' ','-')
    id=id.replace('.','-').lower()
    db.insert({"id": id, "symbol": symbol})

driver.close()



