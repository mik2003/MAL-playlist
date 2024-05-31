import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def reject_all(driver):
    # Wait until the button is present in the DOM and is visible
    wait = WebDriverWait(driver, 10)
    button = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//button[@aria-label='Reject the use of cookies and other data for the purposes described']",
            )
        )
    )

    # Use JavaScript to click the button
    driver.execute_script("arguments[0].click();", button)


def login(driver, email):
    # Wait until the "Sign in" button is present in the DOM
    wait = WebDriverWait(driver, 10)
    sign_in_button = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[@aria-label='Sign in']")
        )
    )

    # Use JavaScript to click the button
    driver.execute_script("arguments[0].click();", sign_in_button)

    # Wait until the input field is present in the DOM and is visible
    wait = WebDriverWait(driver, 10)
    email_input = wait.until(
        EC.visibility_of_element_located((By.ID, "identifierId"))
    )

    # Input the desired string into the input field
    email_input.send_keys(email)

    # Wait until the "Next" button is present in the DOM
    next_button = wait.until(
        EC.presence_of_element_located((By.ID, "identifierNext"))
    )

    # Use JavaScript to click the "Next" button
    driver.execute_script("arguments[0].click();", next_button)


if __name__ == "__main__":
    # Initialize a headless Firefox browser.
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    # Define the user agent string you want to use
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"
    options.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(options=options)

    driver.get("https://www.youtube.com/")

    reject_all(driver)
    # login(driver, "michelangelosecondo@gmail.com")

    # Optionally, you can also perform the click using ActionChains
    # actions = ActionChains(driver)
    # actions.move_to_element(button).click().perform()

    # wait = webdriver.WebDriverWait(driver, timeout=2)
    # wait.until(lambda d : revealed.is_displayed())

    # driver.quit()
