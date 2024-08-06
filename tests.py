import unittest
from unittest.mock import patch
from handler import GithubCrawler, SearchType


class Response:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self):
        pass


class TestGithubCrawler(unittest.TestCase):
    def setUp(self):
        self.keywords = ["test", "crawler"]
        self.proxies = ["194.126.37.94:8080", "13.78.125.167:8080"]
        self.search_type = SearchType.REPOSITORY
        self.crawler = GithubCrawler(self.keywords, self.proxies, self.search_type)

        # Mock Response of list items
        with open("content.html") as content_file:
            content = content_file.read()
            response = Response(text=content)
        self.response_list = response

        # Mock Response of single id
        with open("content_repository.html") as content_file:
            content = content_file.read()
            response = Response(text=content)
        self.response_repository = response

    @patch("requests.get")
    def test_get_proxy(self, request_get):
        proxy = self.crawler._get_proxy()
        self.assertIn(proxy["http"], [f"http://{p}" for p in self.proxies])

    @patch("requests.get")
    def test_search_on_github(self, request_get):
        request_get.return_value = self.response_list

        response_content = self.crawler._search_on_github()
        self.assertEqual(self.response_list.text, response_content)

    def test_parse_content(self):
        urls = self.crawler._parse_content(self.response_list.text)
        expected_urls = [
            "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
            "https://github.com/michealbalogun/Horizon-dashboard",
        ]
        self.assertEqual(urls, expected_urls)

    @patch("requests.get")
    def test_get_urls(self, request_get):
        request_get.return_value = self.response_list

        urls = self.crawler.get_urls()
        excepted_urls = [
            {"url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage"},
            {"url": "https://github.com/michealbalogun/Horizon-dashboard"},
        ]
        self.assertEqual(urls, excepted_urls)

    @patch("requests.get")
    def test_get_repository_information(self, request_get):
        request_get.return_value = self.response_repository

        extra_info = self.crawler.get_repository_information("https://api.github.com/repos/test/test-repo")
        excepted = {
            "language_stats": {
                "CSS": "52.0%",
                "HTML": "0.8%",
                "JavaScript": "47.2%",
            },
            "owner": "atuldjadhav"
        }
        self.assertEqual(extra_info, excepted)

    @patch("requests.get")
    def test_get_urls_with_extra_info(self, requests_get):
        requests_get.side_effect = [self.response_list, self.response_repository, Response(text="")]

        urls_with_info = self.crawler.crawl()
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
