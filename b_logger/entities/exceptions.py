try:
    from selenium.common import WebDriverException
except ImportError:
    WebDriverException = Exception

possible_exceptions = (Exception, WebDriverException)
