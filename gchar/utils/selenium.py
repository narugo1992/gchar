import shutil
from functools import lru_cache
from typing import Optional
from urllib.request import getproxies

PROXIES = getproxies()


@lru_cache()
def _get_faker():
    from faker import Faker
    return Faker()


def get_chromedriver() -> Optional[str]:
    executable_path = shutil.which("chromedriver")
    if executable_path is None:
        from webdriver_manager.dispatch import get_browser_manager
        executable_path = get_browser_manager('chrome').driver_executable

    return executable_path


def _get_chrome_option(headless: bool = False):
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

    options.add_argument("--user-agent=" + _get_faker().user_agent())
    if "all" in PROXIES:
        options.add_argument(f"--proxy-server={PROXIES['all']}")
    elif "https" in PROXIES:
        options.add_argument(f"--proxy-server={PROXIES['https']}")
    elif "http" in PROXIES:
        options.add_argument(f"--proxy-server={PROXIES['http']}")
    else:
        options.add_argument('--proxy-server="direct://"')
        options.add_argument("--proxy-bypass-list=*")

    return options


def get_chrome(headless: bool = False):
    from selenium.webdriver import DesiredCapabilities
    from selenium import webdriver

    caps = DesiredCapabilities.CHROME.copy()
    caps["goog:loggingPrefs"] = {
        "performance": "ALL"
    }  # enable performance logs

    return webdriver.Chrome(
        executable_path=get_chromedriver(),
        options=_get_chrome_option(headless),
        desired_capabilities=caps,
    )
