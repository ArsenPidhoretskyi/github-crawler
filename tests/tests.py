import os
import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from app.handler import GithubCrawler, SearchType


class TestGithubCrawler(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.proxies = ["194.126.37.94:8080", "13.78.125.167:8080"]
        self.crawler = GithubCrawler(self.proxies)

        self.keywords = ["test", "crawler"]
        self.search_type = SearchType.REPOSITORY

        # Mock Response of list items
        with open(os.path.join("tests", "data", "repositories_list.html")) as content_file:
            self.response_list = content_file.read()

        # Mock Response of single id
        with open(os.path.join("tests", "data", "single_repository.html")) as content_file:
            self.response_repository = content_file.read()

    @staticmethod
    def _override_create_response(request_invoke: MagicMock, *contents: str):
        iterator = iter(contents)

        def side_effect_with_default(*args, **kwargs):
            return next(iterator, "")

        response = AsyncMock()
        response.raise_for_status = MagicMock()
        response.text = AsyncMock(side_effect=side_effect_with_default)
        request_invoke.return_value.__aenter__.return_value = response

    @patch("aiohttp.ClientSession.get")
    async def test_search_on_github(self, request_get):
        self._override_create_response(request_get, self.response_list)

        response_content = await self.crawler._search_on_github(["nova"], SearchType.REPOSITORY)
        self.assertEqual(self.response_list, response_content)

    def test_parse_content(self):
        urls = self.crawler._parse_content(self.response_list, SearchType.REPOSITORY)
        expected_urls = [
            "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
            "https://github.com/michealbalogun/Horizon-dashboard",
        ]
        self.assertEqual(urls, expected_urls)

    @patch("aiohttp.ClientSession.get")
    async def test_get_urls(self, request_get):
        self._override_create_response(request_get, self.response_list)

        urls = await self.crawler._get_urls(["nova"], SearchType.REPOSITORY)
        excepted_urls = [
            {"url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage"},
            {"url": "https://github.com/michealbalogun/Horizon-dashboard"},
        ]
        self.assertEqual(urls, excepted_urls)

    @patch("aiohttp.ClientSession.get")
    async def test_get_repository_information(self, request_get):
        self._override_create_response(request_get, self.response_repository)

        extra_info = await self.crawler.get_repository_information("https://api.github.com/repos/test/test-repo")
        excepted = {
            "language_stats": {
                "CSS": "52.0%",
                "HTML": "0.8%",
                "JavaScript": "47.2%",
            },
            "owner": "atuldjadhav"
        }
        self.assertEqual(extra_info, excepted)

    @patch("aiohttp.ClientSession.get")
    async def test_get_urls_extra_info_is_not_returned(self, request_get):
        self._override_create_response(request_get, self.response_list, self.response_repository)

        urls_with_info = await self.crawler.crawl(["nova"], SearchType.ISSUE)
        expected_response = [
            {
                "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
            },
            {
                "url": "https://github.com/michealbalogun/Horizon-dashboard",
            },
        ]
        self.assertEqual(urls_with_info, expected_response)

    @patch("aiohttp.ClientSession.get")
    async def test_get_urls_with_extra_info(self, request_get):
        self._override_create_response(request_get, self.response_list, self.response_repository)
        urls_with_info = await self.crawler.crawl(["nova"], SearchType.REPOSITORY)
        expected_response = [
            {
                "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
                "extra": {
                    "owner": "atuldjadhav",
                    "language_stats": {
                        "CSS": "52.0%",
                        "JavaScript": "47.2%",
                        "HTML": "0.8%"
                    }
                }
            },
            {
                "url": "https://github.com/michealbalogun/Horizon-dashboard",
                "extra": {"owner": "", "language_stats": {}}
            }
        ]
        self.assertEqual(urls_with_info, expected_response)


if __name__ == "__main__":
    unittest.main()
