from enum import Enum
import requests
from bs4 import BeautifulSoup
import random
import json
from typing import List, Dict


class SearchType(Enum):
    REPOSITORY = "repositories"
    ISSUE = "issues"
    WIKI = "wikis"

    @property
    def identifier(self) -> str:
        mapping = {
            SearchType.REPOSITORY: "dheQRw",
            SearchType.ISSUE: "dheQRw",
            SearchType.WIKI: "dheQRw",
        }
        return mapping[self]

    @property
    def block_identifier(self) -> str:
        mapping = {
            SearchType.REPOSITORY: "bBwPjs",
            SearchType.ISSUE: "bBwPjs",
            SearchType.WIKI: "bBwPjs",
        }
        return mapping[self]


class GithubCrawler:
    GITHUB_URL = "https://github.com/search"
    HEADERS_RESPONSE_HTML = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
    LANGUAGE_STATS_SEARCH_ATTRS = {
        "data-ga-click": "Repository, language stats search click, location:repo overview"
    }

    def __init__(self, keywords: List[str], proxies: List[str], search_type: SearchType):
        self._keywords = keywords
        self._proxies = proxies
        self._search_type = search_type

    def _get_proxy(self) -> Dict[str, str]:
        if not self._proxies:
            return {}

        proxy = random.choice(self._proxies)
        return {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}",
        }

    def _search_on_github(self) -> str:
        query = "+".join(self._keywords)
        params = {
            "q": query,
            "type": self._search_type.value.lower(),
        }
        proxy = self._get_proxy()
        response = requests.get(
            self.GITHUB_URL,
            params=params,
            proxies=proxy,
            headers=self.HEADERS_RESPONSE_HTML,
        )
        response.raise_for_status()
        return response.text

    def _parse_content(self, content: str) -> List[str]:
        soup = BeautifulSoup(content, "html.parser")
        return [
            f"https://github.com{item['href']}"
            for block in soup.find_all("div", class_=self._search_type.block_identifier)
            for item in block.find_all("a", class_=self._search_type.identifier)
        ]

    def get_urls(self) -> List[Dict[str, str]]:
        content = self._search_on_github()
        urls = self._parse_content(content)
        return [{"url": url} for url in urls]

    def get_repository_information(self, repo_url: str) -> Dict[str, str]:
        proxy = self._get_proxy()
        response = requests.get(repo_url, proxies=proxy)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        languages_stats = {}
        for language_stat in soup.find_all("a", attrs=self.LANGUAGE_STATS_SEARCH_ATTRS):
            language, percentage = language_stat.find_all("span")
            if language and percentage:
                languages_stats[language.get_text(strip=True)] = percentage.get_text(strip=True)

        owner_span = soup.find("span", class_="author flex-self-stretch")
        owner = owner_span.get_text(strip=True) if owner_span else ""
        return {"owner": owner, "language_stats": languages_stats}

    def crawl(self) -> List[Dict[str, Dict[str, str]]]:
        urls = self.get_urls()
        if self._search_type != SearchType.REPOSITORY:
            return urls

        for url_dict in urls:
            extra_info = self.get_repository_information(url_dict["url"])
            url_dict["extra"] = extra_info

        return urls


# Usage example:
if __name__ == "__main__":
    input_data = {
        "keywords": ["openstack", "nova", "css"],
        "proxies": [],  # ["171.231.28.200:49236", "181.188.27.162:8080"],
        "type": SearchType.REPOSITORY,
    }

    crawler = GithubCrawler(input_data["keywords"], input_data["proxies"], input_data["type"])
    result = crawler.crawl()
    print(json.dumps(result, indent=2))
