import logging

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Requester():
    def __init__(self, config: dict):
        """
        Constructor
        @param config the configuration to load options from
        """
        # Get the logger
        self.logger = logging.getLogger(config["log"]["name"])
        # Set up firefox to run in headless mode to avoid graphical overhead
        options = FirefoxOptions()
        options.set_headless(True)
        # Configure profile settings
        profile = FirefoxProfile()
        # Add the proxy if applicable
        if config["mode"] == "tor":
            profile.set_preference("network.proxy.type", 1)
            profile.set_preference("network.proxy.socks", "127.0.0.1")
            profile.set_preference("network.proxy.socks_port", 9050)
            profile.set_preference("network.proxy.socks_remote_dns", True)
        # Store configs, the profile and options
        self.retries = config["firefox"]["retries"]
        self.page_timeout = config["firefox"]["page_timeout"]
        self.options = options
        self.profile = profile
        # Set driver to None for now
        self.driver = None

    def __enter__(self):
        """
        Run at the beginning of a `with` block
        @returns self
        Initializes the webdriver
        """
        # Build a Firefox webdriver
        self.driver = webdriver.Firefox(self.profile, firefox_options=self.options)
        # Set timeouts
        self.driver.set_page_load_timeout(self.page_timeout)
        # self.driver.implicitly_wait(self.page_timeout)
        return self
    def __exit__(self, typ, value, traceback):
        """
        Run at the end of a `with` block

        Closes the webdriver
        """
        # Close the webdriver
        self.driver.close()
        # Nullify the reference
        self.driver = None

    def request(self, url: str, clear_cookies: bool = False) -> bool:
        """
        Makes a request using the webdriver
        
        @param driver the webdriver to use
        @param url the url to request
        @param retries the number of times to retry
        @return whether the request succeeded
        """
        success = False
        # Make a get request to the tor process
        for retry in range(1, self.retries):
            try:
                # Request the page
                self.driver.get(url)
                # If we get here, the request succeeded
                success = True
                # Log the title of whatever loaded
                self.logger.debug("Title of loaded page: {}".format(self.driver.title))
                # Break out of the retry loop
                break
            # Ignore broken pipe and try again
            except BrokenPipeError as _:
                self.logger.error(
                    "Geckodriver had a broken pipe error. Retrying request ({}/{})".format(
                        retry + 1,
                        self.retries
                    )
                )
                continue 
            # Ignore other exceptions, since we'll allow timeout
            # TODO: look deeper into this
            except Exception as exc:
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG, "body")))
                except Exception as e:
                    self.logger.error("{}".format(e))
                self.logger.error("Failed to request {}: {}".format(url, exc))
                break
        # Clean the driver
        self.cleanup(clear_cookies)
        # Return the final status
        return success
    
    def cleanup(self, clear_cookies: bool):
        """
        Cleans the driver for future requests
        """
        # Perform cleanup
        try:
            # Go to blank page so residual requests dont persist
            self.driver.get("about:blank")
            # Clear cookies if told to
            if clear_cookies:
                self.driver.clear_all_cookies()
        except Exception as exc:
            self.logger.error("Failed to cleanup: {}".format(url, exc))
