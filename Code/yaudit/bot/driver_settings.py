from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from fake_useragent import UserAgent
import os

presence = EC.presence_of_element_located
visible = EC.visibility_of_element_located
clickable = EC.element_to_be_clickable
run_headless = os.getenv('YAUDIT_RUN_HEADLESS', 'false') == 'true'
use_remote_chrome = os.getenv('YAUDIT_RUN_HEADLESS', 'false' if run_headless else 'true') == 'true'


def chrome_options():
    options = Options()
    options.add_argument('--incognito')
    if run_headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument('--window-size=2560,1440')
    options.add_argument("--start-maximized")
    options.add_argument(f'user-agent={UserAgent().chrome}')
    chrome_prefs = {"profile.default_content_settings": {"images": 2}}
    options.experimental_options["prefs"] = chrome_prefs
    options.add_extension(os.path.join('/', 'app', 'yaudit', 'bot', 'extensions', 'adblock.crx'))
    return options


def initialize_driver():
    options = chrome_options()
    if use_remote_chrome:
        chrome_port = os.getenv('CHROME_PORT', 4444)
        driver = webdriver.Remote(f"http://127.0.0.1:{chrome_port}/wd/hub", DesiredCapabilities.CHROME, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(30)
    driver.get("chrome://extensions/?id=cjpalhdlnbpafiamejdnhcphjbkeiagm")
    driver.execute_script("return document.querySelector('extensions-manager').shadowRoot.querySelector('#viewManager > extensions-detail-view.active').shadowRoot.querySelector('div#container.page-container > div.page-content > div#options-section extensions-toggle-row#allow-incognito').shadowRoot.querySelector('label#label input').click()");

    wait = WebDriverWait(driver, 30, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException))
    stale_element_wait = WebDriverWait(driver, 10, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException))

    return driver, wait, stale_element_wait
