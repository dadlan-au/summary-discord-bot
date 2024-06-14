from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import get_config

config = get_config()


def generate_screenshot_file(source_file: Path, screenshot_path: Path):
    """
    Creates a table image based on the subnet columns
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument(
        f"--window-size={config.RENDER_TIX_SCREEN_WIDTH},{config.RENDER_TIX_SCREEN_HEIGHT}"
    )

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )

    driver.get(f"file://{source_file.absolute()}")

    element_present = EC.presence_of_element_located((By.TAG_NAME, "body"))
    WebDriverWait(driver, config.RENDER_TIX_WAIT_TIMEOUT).until(element_present)

    driver.save_screenshot(screenshot_path)

    driver.quit()
