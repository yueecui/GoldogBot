#简单赋值
from selenium.webdriver import Chrome

driver = Chrome()
driver.get('http://www.baidu.com')
form = driver.find_element('id', 'form')
form.screenshot('baidu_form.png')

driver.quit()
