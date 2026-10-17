import os
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = os.environ.get("STREAMLIT_APP_URL", "https://country-faceoff.streamlit.app/")
WAKE_BUTTON = "//button[contains(text(),'Yes, get this app back up')]"

options = Options()
for arg in [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--window-size=1920,1080",
]:
    options.add_argument(arg)

driver = webdriver.Chrome(options=options)
try:
    driver.get(URL)
    print(f"Opened {URL}")
    try:
        button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, WAKE_BUTTON))
        )
        button.click()
        print("App was asleep - clicked wake button")
        WebDriverWait(driver, 20).until(
            EC.invisibility_of_element_located((By.XPATH, WAKE_BUTTON))
        )
    except TimeoutException:
        print("No wake button found - app already awake")
    # Stay on the page so the session registers as real traffic
    time.sleep(45)
    print("Done")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    driver.quit()
