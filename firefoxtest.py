import requests

from selenium.webdriver import Firefox
from time import sleep
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import json
from random import choice, randint
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.webdriver import FirefoxProfile


def selenium_bypass_captcha(driver):
    #  basic code for handling captcha
    #  this requires the user to actually solve the captcha and then continue
    try:
        driver.switch_to_frame(driver.find_element_by_xpath('//iframe[@title="recaptcha widget"]'))
        driver.find_element_by_class_name('recaptcha-checkbox-checkmark').click()
        print('solve captcha ( pop up only ) and press enter to continue')
        input()
        driver.switch_to_default_content()
        driver.find_element_by_id('submit').click()
    except Exception:
        pass


def get_page_selenium(driver, page_url):
    driver.get(page_url)
    # selenium_bypass_captcha(driver)
    return driver.page_source

# session = requests.Session()


firefox_profile = FirefoxProfile()
driver = Firefox(firefox_profile)
driver.implicitly_wait(2)


page_url = "https://www.redfin.com/zipcode/01028/filter/sort=lo-days"
page_url = "https://www.zillow.com/homes/01028_rb/"


tt = get_page_selenium(driver, page_url)

filepath = r"D:\Documents\git\House-Web-Scraping\zillow_html_test.html"
with open(filepath, "w", encoding="utf-8") as f:
    f.write(tt)

