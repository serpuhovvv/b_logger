from abc import ABC, abstractmethod
import importlib



class BrowserAdapter(ABC):
    @abstractmethod
    def make_screenshot(self) -> bytes:
        ...


class SeleniumAdapter(BrowserAdapter):
    def __init__(self, driver):
        self.driver = driver

    def make_screenshot(self) -> bytes:
        return self.driver.get_screenshot_as_png()

    @classmethod
    def is_valid(cls, obj) -> bool:
        try:
            selenium_module = importlib.import_module("selenium.webdriver.ie.webdriver")
            return isinstance(obj, (selenium_module.RemoteWebDriver, selenium_module.WebDriver))
        except ImportError:
            return False


class PlaywrightAdapter(BrowserAdapter):
    def __init__(self, page):
        self.page = page

    def make_screenshot(self) -> bytes:
        pages = self.page.context.pages
        for page in pages:
            try:
                return page.screenshot()
            except Exception:
                pass
        print(f'[ERROR] No valid Playwright page found for screenshot')
        # raise RuntimeError("No valid Playwright page found for screenshot")

    @classmethod
    def is_valid(cls, obj) -> bool:
        try:
            page = importlib.import_module("playwright.sync_api").Page
            return isinstance(obj, page)
        except ImportError:
            return False


ADAPTERS = [SeleniumAdapter, PlaywrightAdapter]


def get_browser_adapter(browser) -> BrowserAdapter:
    for adapter_cls in ADAPTERS:
        if adapter_cls.is_valid(browser):
            return adapter_cls(browser)
    raise RuntimeError(f"Unsupported browser object: {browser}")