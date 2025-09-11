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

    def make_screenshot(self) -> bytes | list | None:
        def try_screenshot(page):
            try:
                if page.is_closed():
                    return None
                return page.screenshot(animations='disabled')
            except Exception as e:
                print(f'[BLogger][WARN] Screenshot failed on page: {getattr(page, 'url', '?')}: {e}')
                return None

        # scr = try_screenshot(self.page)
        # if scr:
        #     return scr
        #
        # try:
        #     for context in self.page.context.browser.contexts:
        #         for other_page in context.pages:
        #             if other_page == self.page:
        #                 continue
        #             scr = try_screenshot(other_page)
        #             if scr:
        #                 return scr
        # except Exception as e:
        #     print(f'[BLogger][WARN] Fallback screenshot iteration failed: {e}')
        #
        # print('[BLogger][WARN] All playwright screenshot attempts failed')
        # return None

        scr_container = []

        try:
            for context in self.page.context.browser.contexts:
                for page in context.pages:
                    scr = try_screenshot(page)
                    if scr:
                        scr_container.append(scr)

            return scr_container[0] if len(scr_container) == 1 else scr_container
        except Exception as e:
            print(f'[BLogger][WARN] Screenshot failed: {e}')

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
