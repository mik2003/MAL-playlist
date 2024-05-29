import random
import time
from typing import Any

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def f7(seq: list[Any]) -> list[Any]:
    """
    Function to remove duplicates in list while maintaining order.

    Parameters
    ----------
    seq : list[Any]

    Returns
    -------
    list[Any]

    See Also
    --------
    Source of the code: https://www.peterbe.com/plog/uniqifiers-benchmark
    """
    seen: set[Any] = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def init_firefox() -> webdriver.firefox.webdriver.WebDriver:
    """Initialize a headless Firefox browser."""
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    return driver


# Function to move the mouse cursor randomly
def random_mouse_movements(driver, duration=5):
    action = ActionChains(driver)
    end_time = time.time() + duration
    while time.time() < end_time:
        x = random.randint(
            0, driver.execute_script("return window.innerWidth")
        )
        y = random.randint(
            0, driver.execute_script("return window.innerHeight")
        )
        action.move_by_offset(x, y).perform()
        time.sleep(
            random.uniform(0.1, 1)
        )  # Random sleep to simulate human behavior


# Function to scroll randomly on the page
def random_scrolling(driver, duration=5):
    end_time = time.time() + duration
    while time.time() < end_time:
        scroll_height = driver.execute_script(
            "return document.body.scrollHeight"
        )
        scroll_position = random.randint(0, scroll_height)
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(
            random.uniform(0.5, 2)
        )  # Random sleep to simulate human behavior


def random_human(driver, duration=2):
    random_scrolling(driver, duration / 2)
    random_mouse_movements(driver, duration / 2)


# Function to click the buttons if they are present
def click_buttons_if_present(driver):
    try:
        # Wait and click the "AGREE" button if present
        agree_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[contains(@class, 'css-47sehv')]/span[text()='AGREE']",
                )
            )
        )
        agree_button.click()
        time.sleep(random.uniform(1, 3))  # Random sleep after clicking

    except Exception as e:
        print("AGREE button not found:", e)

    try:
        # Wait and click the "OK" button if present
        ok_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[text()='OK']"))
        )
        ok_button.click()
        time.sleep(random.uniform(1, 3))  # Random sleep after clicking

    except Exception as e:
        print("OK button not found:", e)
