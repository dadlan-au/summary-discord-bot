import io
import time
from pathlib import Path
from typing import List

from config import get_config
from dpn_pyutils.common import get_logger
from PIL import Image
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

config = get_config()

log = get_logger(__name__)


def get_chromedriver_options() -> Options:
    """
    Gets a set of chromedriver options
    """

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        f"--window-size={config.RENDER_TIX_SCREEN_WIDTH},{config.RENDER_TIX_SCREEN_HEIGHT}"
    )

    return options


def get_chromedriver_service() -> ChromeService:
    """
    Gets a chromedriver service
    """

    return ChromeService(
        ChromeDriverManager(
            driver_version=config.RENDER_TIX_CHROMEDRIVER_VERSION
        ).install()
    )


def get_chromedriver(options: Options, service: ChromeService) -> Chrome:
    """
    Gets a chromedriver
    """

    return Chrome(service=service, options=options)


def generate_screenshot_file(source_file: Path, screenshot_path: Path):
    """
    Creates a table image based on the subnet columns
    """

    driver = get_chromedriver(get_chromedriver_options(), get_chromedriver_service())

    driver.get(f"file://{source_file.absolute()}")

    element_present = EC.presence_of_element_located((By.TAG_NAME, "body"))
    WebDriverWait(driver, config.RENDER_TIX_WAIT_TIMEOUT).until(element_present)

    driver.save_screenshot(screenshot_path)

    driver.quit()


def generate_screenshot_animation_key_frames(
    source_file: Path, num_pages: int
) -> List[bytes]:
    """ """
    driver = get_chromedriver(get_chromedriver_options(), get_chromedriver_service())

    driver.get(f"file://{source_file.absolute()}")

    element_present = EC.presence_of_element_located((By.TAG_NAME, "body"))
    WebDriverWait(driver, config.RENDER_TIX_WAIT_TIMEOUT).until(element_present)

    images = []
    for i in range(num_pages):
        driver.execute_script(f"showPage({i})")
        time.sleep(0.1)
        images.append(driver.get_screenshot_as_png())

    return images


def generate_screenshot_animation(
    source_file: Path, screenshot_file: Path, num_pages: int
):
    """

    Creates an animated, scrolling table image based on the subnet columns
    """

    images = generate_screenshot_animation_key_frames(source_file, num_pages)

    encoded_images = []
    for image in images:
        encoded_images.append(Image.open(io.BytesIO(image)))

    encoded_images[0].save(
        screenshot_file.absolute(),
        save_all=True,
        append_images=encoded_images[1:],
        loop=0,
        duration=config.RENDER_TIX_DELAY_INTERVAL_MS,
    )
