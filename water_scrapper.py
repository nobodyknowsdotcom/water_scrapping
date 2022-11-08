from bs4 import BeautifulSoup
import selenium
import time
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--incognito")
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

link_1 = 'https://artvod.ru/catalog/lider19-2/'
link_2 = 'https://l-w.ru/catalog/voda/voda_19l/'

def get_prices_artvod(soup: BeautifulSoup):
    result = []
    table_rows = soup.select_one('tbody').find_all('tr')
    
    for e in table_rows[:2]:
        raw_price = e.find_all('td')[-1].text.strip()
        result.append(re.sub("[^0-9]", "", raw_price))
    
    return result

def get_price_lw(soup : BeautifulSoup):
    raw_price = soup.find('div', {'class':'card-info'}).find('div', {'class':'price--current'}).text.strip()
    return re.sub("[^0-9]", "", raw_price)

def try_to_prevent_ad(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, ".fancybox-close-small").click()
    except:
        pass

def click_minus_button(driver):
    driver.find_element(By.CSS_SELECTOR, ".counter__btn--minus").click()


driver.get(link_1)
# Ждем, пока загрузится блок с ценами
try:
    btn = WebDriverWait(driver, 10).until(
        lambda wd: wd.find_element(By.TAG_NAME, 'td'))
except selenium.common.TimeoutException:
    print('Can`t found `td` tag on %s page!'%link_1)
    driver.close()
    exit()

# Забираем цену
artvod_prices = get_prices_artvod(BeautifulSoup(driver.page_source, 'lxml'))

driver.get(link_2)
# Ждем, пока загрузится информация о товаре
try:
    btn = WebDriverWait(driver, 10).until(
        lambda wd: wd.find_element(By.CSS_SELECTOR, '.card-info'))
except selenium.common.TimeoutException:
    print('Can`t found `card-info` tag on %s page!'%link_2)
    driver.close()
    exit()

# Чекаем рекламу и забираем цену за две бутылки
try_to_prevent_ad(driver)
two_bottles_lw = get_price_lw(BeautifulSoup(driver.page_source, 'lxml'))
# Закрываем рекламу, уменьшаем кол-во бутылок и забираем цену за одну бутылку
try_to_prevent_ad(driver)
time.sleep(1)
click_minus_button(driver)
one_bottle_lw = get_price_lw(BeautifulSoup(driver.page_source, 'lxml'))

print('\nОдна бутылка на l-w.ru: %s \nДве бутылки на l-w.ru: %s'%(one_bottle_lw, two_bottles_lw))
print('-----')
print('Одна бутылка на artvod.ru: %s \nДве бутылки на artvod.ru: %s'%(artvod_prices[0], artvod_prices[1]))

driver.close()