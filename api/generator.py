from api.errors import NoCache
import re
import threading
import time

from cachetools import TTLCache
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class PayloadGenerator:
    def __init__(
        self, binary_path: str, webdriver_path: str, web_url: str, api_url: str
    ) -> None:
        caps = DesiredCapabilities.CHROME
        caps["goog:loggingPrefs"] = {"performance": "ALL"}

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options._binary_location = binary_path

        self.driver = webdriver.Chrome(
            webdriver_path,
            keep_alive=False,
            desired_capabilities=caps,
            options=options,
        )

        # Regex for filtering data
        self.payload_id_regex = re.compile('"postData":"{\\\\"id\\\\":[\d]{3}}"')
        self.number_regex = re.compile("[\d]{3}")

        # URLs
        self.api_url = api_url
        self.web_url = web_url

        # Cache
        self.payload_id_cache = TTLCache(1, 200)

        # Background Tasks
        thread = threading.Thread(target=self._background_updater, args=())
        thread.daemon = True
        thread.start()

    def _background_updater(self) -> None:
        while True:
            self._fetch_payload_id()
            time.sleep(60)

    def get_logs(self) -> str:
        self.driver.get(self.web_url)
        time.sleep(10)

        logs = self.driver.get_log("performance")
        return (''.join([log.get('message') for log in logs if self.api_url in log.get('message')]))

    def _fetch_payload_id(self) -> int:
        log = self.get_logs()
        match = self.payload_id_regex.findall(log)[0]
        payload_id = int(self.number_regex.findall(match)[0])

        self.payload_id_cache["payload_id"] = payload_id
        return payload_id

    def update_payload_id(self) -> None:
        thread = threading.Thread(target=self._fetch_payload_id, args=())
        thread.daemon = True
        thread.start()

    def get_payload_id(self) -> int:
        payload_id = self.payload_id_cache.get("payload_id")

        if not payload_id:
            raise NoCache()

        return payload_id
